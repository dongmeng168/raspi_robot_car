#coding:utf8
import RPi.GPIO as GPIO
import time


from random import random,choice
from threading import Thread
from copy import copy

import logging


class MyCarLog(object):
    """docstring for MyCarLog"""
    def __init__(self):
        pass
        # 创建Logger
        self.logger = logging.getLogger("MyCar.main")
        self.logger.setLevel(logging.DEBUG)

        # 创建Handler

        # 终端Handler
        self.consoleHandler = logging.StreamHandler()
        self.consoleHandler.setLevel(logging.DEBUG)

        # 文件Handler
        self.fileHandler = logging.FileHandler('log.log', mode='w', encoding='UTF-8')
        self.fileHandler.setLevel(logging.NOTSET)

        # Formatter
        # self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.formatter = logging.Formatter('%(asctime)s - %(message)s')
        self.consoleHandler.setFormatter(self.formatter)
        self.fileHandler.setFormatter(self.formatter)

        # 添加到Logger中
        self.logger.addHandler(self.consoleHandler)
        self.logger.addHandler(self.fileHandler)
    def debug(self,msg):
        return self.logger.debug(msg)
    def info(self,msg):
        return self.logger.info(msg)
    def warning(self,msg):
        return self.logger.warning(msg)
    def error(self,msg):
        return self.logger.error(msg)
    def critical(self,msg):
        return self.logger.critical(msg)

class TraceStatus(object):
    def __init__(self, ori_fun):
        self.ori_fun = ori_fun
    def __call__(self):
        print("decorator start")
        self.ori_fun()
        print("decorator end")



class MyCar(object):
    """docstring for MyCar"""
    def __init__(self):
        """
        定义pwm参数，forward为前进时最高占空比，前进时占空比从转弯占空比开始到前进时最高占空比
        turn为转弯时占空比，转弯采用不变的占空比
        前进和转弯分别定义左边有右边占空比，为方便调节两边的速度
        pwm_hz为频率
        """
        self.pwm_dc_forward_left = 100
        self.pwm_dc_forward_right = 80
        self.pwm_dc_turn_left = 30
        self.pwm_dc_turn_right = 30
        self.pwm_hz = 100

        # L298n模块pwm信号引脚
        self.pwm_pin = (16,18)

        # L298n模块控制信号引脚
        self.en_pin = (11,12,13,15)

        # 前进，左转，右转,停止，模式对应L298n模块使能引脚状态
        self.forward_status = (1,0,1,0)
        self.turn_left_status = (0,1,1,0)
        self.turn_right_status = (1,0,0,1)
        self.stop_status = (0,0,0,0)
        self.back_status = (0,1,0,1)

        # 前进时加速到最大速度时间，减速时减速到转弯速度时间
        self.forward_acc_dec_time = 1.0

        # 声波距离感应器
        # distance_trigger_pin为控制引脚，distance_echo_pin为输入引脚
        # distance_cm为当前距离
        # distance_critical为检测到物体报警距离
        self.distance_trigger_pin = 31
        self.distance_echo_pin = 29
        self.distance_cm = 0
        self.distance_critical = 20
 
        # 存储小车当前状态，初始化为0，前进为1,转向为2，停止为3，后退为4
        self.move_status = 0

        # 小车是否需要停止，该值为真是小车停止（单独线程轮询检测）
        self.stop_signal = False

        # 舵机pwm信号引脚
        self.servo_pin = 7
        # 舵机是否需要转动一圈，初始值为否
        self.servo_turn = False
        # 舵机转到不同角度下物品的距离，右边为负角度，左边为正角度
        # 距离为对应角度下的距离，单位厘米
        self.servo_angle = []
        self.servo_distance = []

        # 定义是否为漫步模式，该模式为前进，遇到障碍物转弯，然后再前进
        self.walk_model = True

        """初始化日志记录类"""
        self.car_log = MyCarLog()

        """调用初始化函数"""
        self.setup()



    def setup(self):
        """设置小车pwm和控制引脚初始化"""
        # 定义引脚号规则，使用BOARD模式
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        # 控制引脚初始化，全部为0，默认初始状态为停止
        for pin in self.en_pin:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        # pwm实例，存放在列表中
        self.pwm_signals = []
        for pin in self.pwm_pin:
            GPIO.setup(pin, GPIO.OUT)
            self.pwm_signals.append(GPIO.PWM(pin, self.pwm_hz))
        # 以 self.pwm_dc_forward 占空比开启pwm信号，默认初始占空比为前进模式占空比
        for pwm_signal in self.pwm_signals:
            pwm_signal.start(self.pwm_dc_forward_left)
        # 设置声波距离感应器
        GPIO.setup(self.distance_trigger_pin,GPIO.OUT)
        GPIO.setup(self.distance_echo_pin,GPIO.IN)
        # 设置舵机pwm引脚
        GPIO.setup(self.servo_pin,GPIO.OUT,initial=False)
        self.senvor_pwm = GPIO.PWM(self.servo_pin,50)
        self.senvor_pwm.start(0)
        # 纪录设置完成到日志中
        self.car_log.info("start_ok,angle=0")

    def forward(self):
        """向前进，通过控制占空比慢慢加速"""
        self.move_status = 1
        # 使能端赋值为前进模式
        GPIO.output(self.en_pin,self.forward_status)
        # 纪录设置完成到日志中
        self.car_log.info("forward,angle=0")

    def pwmTuning(self):
        '''调节pwm值，目的是保持走直线和车启动的加速、停止的减速'''
        deal3 = Thread(target=self.pwmSet)
        deal3.setDaemon(True)
        deal3.start()

    def pwmSet(self):
        '''根据左右轮设置的不同的起始pwm和最大pwm控制车不同状态下的两轮的速度'''
        acc_nums = 20
        delta_left_dc = int((self.pwm_dc_forward_left - self.pwm_dc_turn_left)/acc_nums)
        delta_right_dc = int((self.pwm_dc_forward_right - self.pwm_dc_turn_right)/acc_nums)
        delta_time = self.forward_acc_dec_time/acc_nums 
        acc_flag = True     
        while True:
            # 车是从其他状态切换（acc_flag参数保证）回的前进状态，则加速
            # 以后用陀螺仪保证左右两侧的平衡，需要修改代码
            if self.move_status == 1 and acc_flag :
                acc_flag = False
                dc_now_left = self.pwm_dc_turn_left
                dc_now_right = self.pwm_dc_turn_right
                for acc_num in range(acc_nums):
                    dc_now_left += delta_left_dc
                    dc_now_right += delta_right_dc
                    self.pwm_signals[0].ChangeDutyCycle(dc_now_left)
                    self.pwm_signals[1].ChangeDutyCycle(dc_now_right)
                    time.sleep(delta_time)
            elif self.move_status == 3 :
                # 停车状态，减速停车
                acc_flag = False
                dc_now_left = self.pwm_dc_forward_left
                dc_now_right = self.pwm_dc_forward_right
                for acc_num in range(acc_nums):
                    dc_now_left -= delta_left_dc
                    dc_now_right -= delta_right_dc
                    self.pwm_signals[0].ChangeDutyCycle(dc_now_left)
                    self.pwm_signals[1].ChangeDutyCycle(dc_now_right)
                    time.sleep(delta_time)
            else:
                # 转弯和其他状态
                acc_flag = False
                self.pwm_signals[0].ChangeDutyCycle(self.pwm_dc_turn_left)
                self.pwm_signals[1].ChangeDutyCycle(self.pwm_dc_turn_right)
            time.sleep(0.001)


    def dealStopSignal(self):
        """线程，处理小车停止信号的线程"""
        while True:
            if self.stop_signal:                
                # 使能端赋值为停止模式
                GPIO.output(self.en_pin,self.stop_status)
                self.move_status = 3
                # self.car_log.info("stop,angle=0")
            time.sleep(0.01)

    def turn(self,angle):
        """转弯，参数为角度"""
        self.move_status = 2
        # 通过一个简单的公式计算角度和转弯时间，不准确，打算用陀螺仪实现精确转弯
        angle = int(abs(angle) % 360)
        # 计算转弯时间
        turn_time = self.calaTurnTime(angle)
        # 转弯角度小于180，右转弯；大于180，左转弯
        # 给10度的容错差，转的角度小于10度就不转弯
        if angle >9 and angle <= 180:
            # 右转
            GPIO.output(self.en_pin,self.turn_right_status)
            time.sleep(turn_time)
        if angle > 180 and angle < 351:
            # 左转
            GPIO.output(self.en_pin,self.turn_left_status)
            time.sleep(turn_time)
        self.car_log.info("turn,angle=%s" % str(angle))

    def backup(self):
        """后退，pwm采用转弯模式"""
        self.move_status = 4
        # 使pwm占空比为转弯模式
        self.pwm_signal[0].ChangeDutyCycle(self.pwm_dc_turn_left)
        self.pwm_signal[1].ChangeDutyCycle(self.pwm_dc_turn_right)
        GPIO.output(self.en_pin,self.back_status)
        self.car_log.info("backup,angle=0")

    def listenStopSignal(self):
        """调用线程监听小车收否需要停止信号stop_signal"""
        print('listenStopSignal start...')
        deal2 = Thread(target=self.dealStopSignal)
        deal2.setDaemon(True)
        deal2.start()

    def calaTurnTime(self,angle):
        """根据输入的角度计算转弯时间"""
        turn_time = angle*5/1000.0
        self.car_log.info("calaTurnTime,angle=%s,time=%s" % (angle,turn_time))
        return turn_time

    def shutDown(self):
        '''因为--del--回收机制不好用，采用自定义程序处理收尾工作'''
        for pwm_signal in self.pwm_signals:
            pwm_signal.stop()
        GPIO.cleanup()
        self.car_log.info("shutDown,angle=0")

    def getDistance(self):
        '''线程，根据超声波模块计算距离'''
        while True:
            # 发送一个触发信号，开始发送超声波测距
            GPIO.output(self.distance_trigger_pin,True)
            time.sleep(0.0001)
            GPIO.output(self.distance_trigger_pin,False)
            # 获得开始时间，电平为1
            count = 10000
            while GPIO.input(self.distance_echo_pin) != True and count>0:
                count = count-1
            start = time.time()
            # 获得结束时间，电平为0
            count = 10000
            while GPIO.input(self.distance_echo_pin) != False and count>0:
                count = count-1    
            finish = time.time()
            # 根据时间计算距离
            pulse_len = finish-start
            self.distance_cm = pulse_len/0.000058
            time.sleep(0.001)     

    def listenDistance(self):
        '''调用线程监听超声波距离感应器的数值'''
        print('listenDistance start...')
        deal3 = Thread(target=self.getDistance)
        deal3.setDaemon(True)
        deal3.start()

    def servoTurn(self):
        '''线程，当变量servo_turn为真时，转动电机一圈，并且将servo_turn的值设为假'''
        # turn around is [0,-90],[-90,0],[0,90],[90,0]
        while True:
            if self.servo_turn :
                self.servo_turn = False
                pwm1= []
                pwm2=[]
                pwm3=[]
                pwm4=[]
                for angle in range(0,90,9):
                    pwm1.append(7.5 + (-1 * angle)/18.0)
                    pwm2.append(7.5 + (angle - 90)/18.0)
                    pwm3.append(7.5 + angle/18.0)
                    pwm4.append(7.5 + (90 - angle)/18.0)
                pwm_all = pwm1+pwm2+pwm3+pwm4+[7.5]

                pwm_all.remove(2.5)
                pwm_all.remove(12.5)

                for num in range(len(pwm_all)):
                    # print(num,pwm_all[num])
                    self.senvor_pwm.ChangeDutyCycle(pwm_all[num])
                    time.sleep(0.12)
                    # 第10-28个元素为从-90度到90度的范围
                    # 在这个范围读取超声波距离，并将角度和距离分别写入变量
                    if num >= 10 and num <= 28:
                        angle = (pwm_all[num]-7.5)*18
                        # print('self.distance_cm=',self.distance_cm,angle)
                        self.servo_angle.append(angle)
                        self.servo_distance.append(self.distance_cm)
                self.senvor_pwm.ChangeDutyCycle(0)

    def listenServoTurn(self):
        '''调用线程监听servo_turn变量是否为真，为真则转动舵机'''
        print('listenServoTurn start...')
        deal4 = Thread(target=self.servoTurn)
        deal4.setDaemon(True)
        deal4.start()  


if __name__ == '__main__':
    car1 = MyCar()
    # 监听距离感应器
    car1.listenDistance()
    # 监听停止信号
    car1.listenStopSignal()
    # 监听舵机转动信号
    car1.listenServoTurn()
    # car1.pwmTuning()

    # # print('moving start...')
    # # s1 = time.time()

    # car1.forward()

    # # car1.turn(280)

    # car1.servo_turn = True


    time.sleep(5)



    # for num in range(len(car1.servo_angle)):
    #     print(car1.servo_angle[num],car1.servo_distance[num])

    car1.stop_signal = True
    # s2 = time.time()


    car1.shutDown()

    # print(s2-s1)
    print("all done")

