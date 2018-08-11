#!/usr/bin/python

import pigpio
P=pigpio.pi()
P.write(13,0)
P.set_servo_pulsewidth(5,1500)
P.set_servo_pulsewidth(6,1500)

