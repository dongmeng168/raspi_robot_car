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
        """定义pwm参数，占空比在前进和转弯时不同，频率为50hz"""

        

        self.pwm_dc_forward_left = 100
        self.pwm_dc_forward_right = 80
        self.pwm_dc_turn_left = 30
        self.pwm_dc_turn_right = 30
        self.pwm_hz = 100

        # pwm信号引脚
        self.pwm_pin = (16,18)

        # 控制信号引脚
        self.en_pin = (11,12,13,15)

        # 前进，左转，右转,停止，模式对应使能引脚状态
        self.forward_status = (1,0,1,0)
        self.turn_left_status = (0,1,1,0)
        self.turn_right_status = (1,0,0,1)
        self.stop_status = (0,0,0,0)
        self.back_status = (0,1,0,1)

        # 前进时加速到最大速度时间，减速时减速时间，均设为1秒
        self.forward_acc_dec_time = 1.0

        # 声波距离感应器
        self.distance_trigger_pin = 31
        self.distence_echo_pin = 29
        self.distance_cm = 0
        self.distance_critical = 20
        # 小车静止时，检测到物体靠近会小车转向再前进，参数为前进时间，单位为秒
        self.sensor_leave_time = 0.1
        # 存储小车当前状态，初始化为0，前进为1,转向为2，停止为3，后退为4
        self.move_status = 0

        self.stop_signal = False

        """初始化日志记录类"""
        self.car_log = MyCarLog()

        """调用初始化函数"""
        self.setup()



    def setup(self):
        """设置小车pwm和控制引脚初始化"""
        # 定义引脚号规则，使用BOARD模式
        GPIO.setmode(GPIO.BOARD)
        # GPIO.setwarnings(False)
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
        # 设置距离感应器，初始状态上拉为高电平，感应器时遇到物品低电平
        GPIO.setup(self.distance_trigger_pin,GPIO.OUT)
        GPIO.setup(self.distence_echo_pin,GPIO.IN)
        # 纪录设置完成到日志中
        self.car_log.info("start_ok,angle=0")

    def forward(self):
        """向前进，通过控制占空比慢慢加速"""
        self.move_status = 1
        # 使能端赋值为前进模式
        GPIO.output(self.en_pin,self.forward_status)

        self.car_log.info("forward,angle=0")

    def pwmTuning(self):
        deal3 = Thread(target=self.pwmSet)
        deal3.setDaemon(True)
        deal3.start()

    def pwmSet(self):
        acc_nums = 20
        delta_left_dc = int((self.pwm_dc_forward_left - self.pwm_dc_turn_left)/acc_nums)
        delta_right_dc = int((self.pwm_dc_forward_right - self.pwm_dc_turn_right)/acc_nums)
        delta_time = self.forward_acc_dec_time/acc_nums 
        acc_flag = True     
        while True:
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
                acc_flag = False
                self.pwm_signals[0].ChangeDutyCycle(self.pwm_dc_turn_left)
                self.pwm_signals[1].ChangeDutyCycle(self.pwm_dc_turn_right)
            time.sleep(0.001)


    def dealStopSignal(self):
        """小车停止"""
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
        # 使pwm占空比为转弯模式

        # self.pwm_signal[0].ChangeDutyCycle(self.pwm_dc_turn_left)
        # self.pwm_signal[1].ChangeDutyCycle(self.pwm_dc_turn_right)

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
        print('listenStopSignal done')
        deal2 = Thread(target=self.dealStopSignal)
        deal2.setDaemon(True)
        deal2.start()

    def calaTurnTime(self,angle):
        """根据输入的角度计算转弯时间"""
        turn_time = angle*5/1000.0
        self.car_log.info("calaTurnTime,angle=%s,time=%s" % (angle,turn_time))
        return turn_time

    def shutDown(self):
        for pwm_signal in self.pwm_signals:
            pwm_signal.stop()
        GPIO.cleanup()
        self.car_log.info("shutDown,angle=0")

    def getDistance(self):

        while True:
            GPIO.output(self.distance_trigger_pin,True)
            time.sleep(0.0001)
            GPIO.output(self.distance_trigger_pin,False)

            count = 10000
            while GPIO.input(self.distence_echo_pin) != True and count>0:
                count = count-1

            start = time.time()

            count = 10000
            while GPIO.input(self.distence_echo_pin) != False and count>0:
                count = count-1    

            finish = time.time()
            pulse_len = finish-start
            self.distance_cm = pulse_len/0.000058

            if self.distance_cm < self.distance_critical:
                GPIO.output(self.en_pin,self.stop_status)

            time.sleep(0.001)     

            # print('listenDistance  ',self.distance_cm)

    def listenDistance(self):
        deal3 = Thread(target=self.getDistance)
        deal3.setDaemon(True)
        deal3.start()
        


if __name__ == '__main__':
    car1 = MyCar()
    car1.listenDistance()
    car1.listenStopSignal()
    car1.pwmTuning()

    # print('moving start...')
    # s1 = time.time()

    # car1.forward()
    time.sleep(20)

    # car1.turn(280)






    car1.stop_signal = True
    # s2 = time.time()


    car1.shutDown()

    # print(s2-s1)
    print("all done")

