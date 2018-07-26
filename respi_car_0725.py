#coding:utf8
import RPi.GPIO as GPIO
import time
from random import random,choice
from threading import Thread
from copy import deepcopy

class MyCar(object):
    """docstring for MyCar"""
    def __init__(self):
        """定义pwm参数，占空比在前进和转弯时不同，频率为50hz"""
        self.pwm_dc_forward = 100
        self.pwm_dc_turn = 60
        self.pwm_hz = 50
        
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

        # 前进时加速到最大速度时间，减速时间初始值为1秒
        self.forward_acc_dec_time = 1

        # 距离感应器，键为感应器所在位置的角度，值对感应器状态，初始为1，没有感应到物体
        self.sensor_pin = (35,36,37,38)
        self.sensor_pin_angle = {35:0,36:90,37:180,38:270}
        self.sensor_angle_status = {0:1,90:1,180:1,270:1}
        # 距离感应器是否感应到物品，1表示没有
        self.sensor_of_things = {0:1,90:1,180:1,270:1}
        # 小车静止时，检测到物体小车转向后再前进时间
        self.sensor_leave_time = 0.1
        # 存储小车当前状态，初始化为0，前进为1,转向为2，停止为3，后退为4
        self.move_status = 0

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
            pwm_signal.start(self.pwm_dc_forward)
        # 设置距离感应器，初始状态上拉为高电平，感应器时遇到物品低电平
        for pin in self.sensor_pin :
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)       

    def forward(self):
        print("forward...")
        """向前进，通过控制占空比慢慢加速"""
        self.move_status = 1
        # 使能端赋值为前进模式
        GPIO.output(self.en_pin,self.forward_status)
        # 慢慢修改占空比从转弯模式为前进模式
        delta_time = self.forward_acc_dec_time*1.0/(self.pwm_dc_forward-self.pwm_dc_turn )
        for dc_now in range(self.pwm_dc_turn,self.pwm_dc_forward+1):
            for pwm_signal in self.pwm_signals:
                pwm_signal.ChangeDutyCycle(dc_now)
            time.sleep(delta_time)



    def stop(self):
        """小车停止"""
        self.move_status = 3
        # 慢慢修改占空比从前进模式到转弯模式，然后停车
        delta_time = self.forward_acc_dec_time*1.0/(self.pwm_dc_forward-self.pwm_dc_turn )
        for dc_now in range(self.pwm_dc_turn,self.pwm_dc_forward+1):
            for pwm_signal in self.pwm_signals:
                pwm_signal.ChangeDutyCycle(self.pwm_dc_turn+self.pwm_dc_forward-dc_now)
            time.sleep(delta_time)
        # 使能端赋值为停止模式
        GPIO.output(self.en_pin,self.stop_status) 

    def turn(self,angle):
        print("turn...")
        """转弯，参数为角度"""
        self.move_status = 2
        # 使pwm占空比为转弯模式
        for pwm_signal in self.pwm_signals:
            pwm_signal.ChangeDutyCycle(self.pwm_dc_turn)

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

    def backup(self):
        print("backup...")
        """后退，pwm采用转弯模式，参数为以秒为单位的时间"""
        self.move_status = 4
        # 使pwm占空比为转弯模式
        for pwm_signal in self.pwm_signals:
            pwm_signal.ChangeDutyCycle(self.pwm_dc_turn)        
        GPIO.output(self.en_pin,self.back_status)


    def calaTurnTime(self,angle):
        """根据输入的角度计算转弯时间"""
        turn_time = angle*3.7/1000.0
        print("turn_time is %s" % str(turn_time))
        return turn_time

    def __del__(self):
        for pwm_signal in self.pwm_signals:
            pwm_signal.stop()
        GPIO.cleanup()


    def listen_sensor(self):
        """监听并用线程处理红外线模块引脚为0的函数"""
        # 监听所有红外线模块引脚
        for pin in self.sensor_pin:
            GPIO.add_event_detect(pin, GPIO.FALLING)
        deal1 = Thread(target=self.deal_sensor)
        deal1.setDaemon(True)
        deal1.start()

    def deal_sensor(self):
        """处理单个或者多个红外线模块引脚为0的函数，用一个线程跑"""
        while True:
            angle_status_dict = deepcopy(self.sensor_angle_status)
            for pin in self.sensor_pin:
                if GPIO.event_detected(pin):
                    angle_status_dict[self.sensor_pin_angle[pin]] = 0
                    self.sensor_of_things[self.sensor_pin_angle[pin]] = 0
            # 遇到物品的引脚sensor_angle_status字典值为0
            # 值为1的为没有遇到物品的方向，随机选取值为1的角度为转向角度
            # 值为1的角度（没有遇到物体的方向）为0个，则原地不动，返回角度0
            angle_list = []
            for key,value in angle_status_dict.items():
                if value == 1:
                    angle_list.append(angle_status_dict[key]) 
            # 如果角度列表为空，表示被围着了，应该停止
            if angle_list:
                self.stop()
            # 角度列表不为空（至少一个模块检测到物品）且是静止状态，则旋转一个角度，向前走一段时间
            if angle_list and self.move_status == 3 :
                # 随机选择一个剩余的作为转的角度
                angle = choice(angle_list)
                self.turn(angle)
                # 向前行驶一段时间,停止
                self.forward()
                time.sleep(self.sensor_leave_time)
                self.stop()
            # 角度列表不为空，且是前进状态，则停止前进
            if angle_list and self.move_status == 1 :
                self.stop()
            # 为了测试时间为0.1，实际使用修改为0.001
            time.sleep(0.1)
            print("deal_sensor runing...")



if __name__ == '__main__':
    car1 = MyCar()
    print(car1.move_status)
    car1.listen_sensor()
    print("MyCar done")


    car1.forward()
    print(car1.move_status)
    time.sleep(1)
    car1.stop()

    car1.turn(60)
    car1.turn(310)
    print(car1.move_status)    
    car1.turn(5)
    car1.turn(359)
    print(car1.move_status)
    car1.turn(22)
    car1.forward()
    time.sleep(0.2)
    car1.stop()
    print(car1.move_status)
    print("done")

