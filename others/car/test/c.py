import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 4
GPIO_ECHO = 17

GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo
GPIO.output(GPIO_TRIGGER, True)
time.sleep(0.25)
GPIO.output(GPIO_TRIGGER, False)
time.sleep(0.00001)
GPIO.output(GPIO_TRIGGER, True)
while GPIO.input(GPIO_ECHO)==0:
  start = time.time()
while GPIO.input(GPIO_ECHO)==1:
  stop = time.time()
distance1 = (stop-start) * 34000/2
  
print "D1:%.1f" % (distance1)
 
GPIO.cleanup()

