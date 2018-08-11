import time
import RPi.GPIO as GPIO
import pigpio

PG=pigpio.pi()

GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 4
GPIO_ECHO = 17

GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo
GPIO.output(GPIO_TRIGGER, True)

time.sleep(0.5)
for x in range(20):
 GPIO.output(GPIO_TRIGGER, False)
 time.sleep(0.00001)
 GPIO.output(GPIO_TRIGGER, True)
 start = time.time()
 i=0
 j=0
 while GPIO.input(GPIO_ECHO)==0:
  i+=1
  start = time.time()
 
 while GPIO.input(GPIO_ECHO)==1:
  stop = time.time()
  j+=1
 
 distance1 = (stop-start) * 34000/2
  
 GPIO.output(GPIO_TRIGGER, False)
 time.sleep(0.00001)
 GPIO.output(GPIO_TRIGGER, True)
 start=0; stop=0 
 w1=PG.wait_for_edge(17,pigpio.RISING_EDGE,1)
 start=time.time()
 w2=PG.wait_for_edge(17,pigpio.FALLING_EDGE,1)
 end=time.time()
 if w1 and w2:
  distance2 = (stop-start)*34000/2
 else:
  distance2=0
 
 print "%d D1:%.1f D2:%.1f  %d  %d" % (x, distance1, distance2, i, j )
 
 time.sleep(0.2)
GPIO.cleanup()

