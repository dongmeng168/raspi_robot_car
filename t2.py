#coding:utf8
from time import sleep


def servoTurn():
    turn_around = [[0,-90],[-90,0],[0,90],[90,0]]

    servo_turn = True

    while servo_turn:
            servo_turn = False
            print(servo_turn)

            pwm1= []
            pwm2=[]
            pwm3=[]
            pwm4=[]

            for angle in range(0,91,9):
                pwm1.append(7.5 + (-1 * angle)/18.0)
                pwm2.append(7.5 + (angle - 90)/18.0)
                pwm3.append(7.5 + angle/18.0)
                pwm4.append(7.5 + (90 - angle)/18.0)
            pwm_all = pwm1+pwm2+pwm3+pwm4

            for pwm in pwm_all:
                print('pwm=',pwm)
                # sleep(0.1)
            # for angle in range(0,91,9):
            #     new_angle = angle - 90
            #     pwm = 7.5 + new_angle/18.0
            #     print('pwm=',pwm,'    angle=',new_angle)
            #     sleep(0.1)
            # for angle in range(0,91,9):
            #     new_angle = angle
            #     pwm = 7.5 + new_angle/18.0
            #     print('pwm=',pwm,'    angle=',new_angle)
            #     sleep(0.1)
            # for angle in range(0,91,9):
            #     new_angle = 90 - angle
            #     pwm = 7.5 + new_angle/18.0
            #     print('pwm=',pwm,'    angle=',new_angle)
            #     sleep(0.1)


servoTurn()