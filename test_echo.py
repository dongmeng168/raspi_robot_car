#!/usr/bin/python3
#coding:utf8
import time
import RPi.GPIO as GPIO

trigger_pin = 31
echo_pin = 29

GPIO.setmode(GPIO.BOARD)
GPIO.setup(trigger_pin,GPIO.OUT)
GPIO.setup(echo_pin,GPIO.IN)

def send_trigger_pulse():
    GPIO.output(trigger_pin,True)
    time.sleep(0.0001)
    GPIO.output(trigger_pin,False)

def wait_for_echo(value,timeout):
    count = timeout
    while GPIO.input(echo_pin) != value and count>0:
        count = count-1

def get_distance():
    send_trigger_pulse()
    wait_for_echo(True,10000)
    start = time.time()
    wait_for_echo(False,10000)
    finish = time.time()
    pulse_len = finish-start
    distance_cm = pulse_len/0.000058
    return distance_cm

while True:
    print("cm = %f"%get_distance())
    time.sleep(1)