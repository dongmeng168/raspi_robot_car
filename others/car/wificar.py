#!/usr/bin/python
#-!- coding: utf-8 -!-
""" This is WiFi Car control class. """
import pigpio,thread,time
import RPi.GPIO as GPIO

class WifiCar:
	
	distance=None # The distance measure approximate 10 times every second.
	
	PG=None  # pigpio object.
	
	LED_RED_PIN=12
	LED_BLUE_PIN=16
	LED_GREEN_PIN=20
	
	SERVO_POWER_PIN=13
	SERVO_UPDOWN_PIN=5
	SERVO_LEFTRIGHT_PIN=6
	SERVO_CENTER=(1500,1620) # Left/Right, Up/Down center 
	SERVO_RANGE=((700,-700),(300,-600)) # servo move range.
	
	L298N_INPUT1_PIN=27
	L298N_INPUT2_PIN=22
	L298N_INPUT3_PIN=23
	L298N_INPUT4_PIN=24
	L298N_ENABLEA_PIN=18
	L298N_ENABLEB_PIN=25
	
	ULTRASONIC_TRIG_PIN=4
	ULTRASONIC_ECHO_PIN=17
	
	def __init__(self, address=None ):
		if address:
			self.PG=pigpio.pi( address )
		else:
			self.PG=pigpio.pi()
		# set L298N state.
		self.PG.set_PWM_dutycycle( self.L298N_ENABLEA_PIN, 0 )
		self.PG.set_PWM_frequency( self.L298N_ENABLEA_PIN, 400) 
		self.PG.set_PWM_range( self.L298N_ENABLEA_PIN, 1000 )
		self.PG.set_PWM_dutycycle( self.L298N_ENABLEB_PIN, 0 )
		self.PG.set_PWM_frequency( self.L298N_ENABLEB_PIN, 400) 
		self.PG.set_PWM_range( self.L298N_ENABLEB_PIN, 1000 )
		self.forward(0)
		# GPIO for ultrasonic distance measure.
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.ULTRASONIC_TRIG_PIN, GPIO.OUT)
		GPIO.setup(self.ULTRASONIC_ECHO_PIN, GPIO.IN)
		GPIO.output(self.ULTRASONIC_TRIG_PIN, GPIO.HIGH)
		# Read distance front of car every 0.1 seconds.
		thread.start_new_thread( self.check_distance, () )
		
	daemon_running=True # Mark of thread running.
	
	def __del__(self):
		self.close()
	
	def feed_dog(self ,pin ):
		'''Use a virtual GPIO pin as dog. '''
		self.PG.write( pin,not self.PG.read(pin) )
	
	def check_distance(self ):
		run_counter=0
		counter_max=5;
		while self.daemon_running:
			if not self.ultrasonic_lock.locked():
				self.ultrasonic_distance()
			# flash green led as distance mark. When long than 2 meter, flash very slow. nearer than faster. 
			if not self.distance or self.distance>150:
				counter_max=12
			elif self.distance>60:
				counter_max=6
			elif self.distance>30:
				counter_max=4
			elif self.distance>15:
				counter_max=2
				# If car is forwarding. then slow down the car.
				# self.slowdown()
			else:
				counter_max=1
				# If car is forwarding. stop the car.
				self.stop(forward=True)
			if run_counter==0:
				self.led('green',True)
			else:
				self.led('green',False)
			run_counter+=1
			if run_counter>=counter_max: run_counter=0
			time.sleep(0.1)
	
	
	def reset(self ):
		# power on servo and set it to the center.
		self.PG.set_servo_pulsewidth( self.SERVO_LEFTRIGHT_PIN, self.SERVO_CENTER[0] )
		self.PG.set_servo_pulsewidth( self.SERVO_UPDOWN_PIN, self.SERVO_CENTER[1] )
		self.PG.write(self.SERVO_POWER_PIN, 0) # power on servo.
		self.forward(0)# stop the car.
		self.led('red',False)
		self.led('blue',False)
		self.led('green',False)
		
	def led(self, color, light=True): 
		''' color is one of 'red','blue','green' '''
		if color and 'red'==color.lower():
			self.PG.write( self.LED_RED_PIN, not light )
		if color and 'blue'==color.lower():
			self.PG.write( self.LED_BLUE_PIN, not light )
		if color and 'green'==color.lower():
			self.PG.write( self.LED_GREEN_PIN, not light )
	
	def inverse_led(self, color): 
		''' Change the LED light on or off '''
		if color and 'red'==color.lower():
			self.PG.write( self.LED_RED_PIN, not self.PG.read( self.LED_RED_PIN ) )
		if color and 'blue'==color.lower():
			self.PG.write( self.LED_BLUE_PIN, not self.PG.read( self.LED_BLUE_PIN ) )
		if color and 'green'==color.lower():
			self.PG.write( self.LED_GREEN_PIN, not self.PG.read( self.LED_GREEN_PIN ) )
	
	# A thread lock for single run of ultrasonic.
	ultrasonic_lock=thread.allocate_lock()
	
	def ultrasonic_distance(self ):
		''' Return distance in centimetre. '''
		self.ultrasonic_lock.acquire()
		GPIO.output( self.ULTRASONIC_TRIG_PIN, GPIO.LOW ) # High pulse 10uS
		time.sleep( 0.00001 )
		GPIO.output( self.ULTRASONIC_TRIG_PIN, GPIO.HIGH )
		start=time.time();stop=None; i=0 # Wait echo raise up.
		while GPIO.input( self.ULTRASONIC_ECHO_PIN )==0 and i<100:start=time.time();i+=1
		# wait echo falling down. max 1500 about 6 meter, out of sensor range.
		while GPIO.input( self.ULTRASONIC_ECHO_PIN )==1 and i<1500:stop=time.time();i+=1 
		if stop and i<1500: # Too far
			self.distance=(stop-start)*34000/2; # There is not temperature calibration.
		else:
			self.distance=None
		self.ultrasonic_lock.release()
		return self.distance
	
	def left_wheel(self, speed):
		if speed>1000:speed=1000
		if speed<-1000:speed=-1000
		if speed==0:
			self.PG.write( self.L298N_INPUT3_PIN, 0 )
			self.PG.write( self.L298N_INPUT4_PIN, 0 )
			self.PG.set_PWM_dutycycle( self.L298N_ENABLEB_PIN, 1000 )
		elif speed>0:
			self.PG.write( self.L298N_INPUT3_PIN, 0 )
			self.PG.write( self.L298N_INPUT4_PIN, 1 )
			self.PG.set_PWM_dutycycle( self.L298N_ENABLEB_PIN, abs(speed) )
		else:
			self.PG.write( self.L298N_INPUT3_PIN, 1 )
			self.PG.write( self.L298N_INPUT4_PIN, 0 )
			self.PG.set_PWM_dutycycle( self.L298N_ENABLEB_PIN, abs(speed) )
		
		
	def right_wheel(self, speed):
		if speed>1000:speed=1000
		if speed<-1000:speed=-1000
		if speed==0:
			self.PG.write( self.L298N_INPUT1_PIN, 0 )
			self.PG.write( self.L298N_INPUT2_PIN, 0 )
			self.PG.set_PWM_dutycycle( self.L298N_ENABLEA_PIN, 1000 )
		elif speed>0:
			self.PG.write( self.L298N_INPUT1_PIN, 0 )
			self.PG.write( self.L298N_INPUT2_PIN, 1 )
			self.PG.set_PWM_dutycycle( self.L298N_ENABLEA_PIN, abs(speed) )
		else:
			self.PG.write( self.L298N_INPUT1_PIN, 1 )
			self.PG.write( self.L298N_INPUT2_PIN, 0 )
			self.PG.set_PWM_dutycycle( self.L298N_ENABLEA_PIN, abs(speed) )
		
	def is_forwarding(self ):
		l=self.PG.get_PWM_dutycycle( self.L298N_ENABLEA_PIN )
		r=self.PG.get_PWM_dutycycle( self.L298N_ENABLEB_PIN )
		if self.PG.read( self.L298N_INPUT3_PIN )==1 and self.PG.read( self.L298N_INPUT4_PIN )==0:
			l=-l # left move backward
		if self.PG.read( self.L298N_INPUT1_PIN )==1 and self.PG.read( self.L298N_INPUT1_PIN )==0:
			r=-r # right move backward
		return l+r>0
			
	def slowdown(self ):
		du=self.PG.get_PWM_dutycycle(  self.L298N_ENABLEB_PIN )
		self.PG.set_PWM_dutycycle(  self.L298N_ENABLEB_PIN, du*0.5 )
	
	def forward(self, speed=350, direction=0 ): # from -1000~1000. 0 mean stop.
		''' Move car forward. '''
		if speed<=0 or self.distance>30: 
			self.left_wheel ( speed+direction )
			self.right_wheel( speed-direction )
		else:  # Before hit something. slow down or stop.
			if self.distance<15:
				speed=0
				self.stop()
			elif self.distance<30:
				speed*=(self.distance-15)/15
				if speed<0:speed=0
				self.left_wheel ( speed+direction )
				self.right_wheel( speed-direction )
		
	def stop(self, forward=False ):
		if forward:
			if self.is_forwarding():
				self.stop()
		else:
			self.left_wheel(0)
			self.right_wheel(0)
		
	def backward(self, speed=350 ): # from -1000~1000
		self.forward(-speed)
		
	def rotate(self, degree ):
		""" Rotate the car in degree """
		pass
		
	def servo_horizontal(self, hor ): 
		''' hor from -1000 to 1000 '''
		if hor<-1000: hor=-1000
		if hor> 1000: hor= 1000
		if hor==0:
			self.PG.set_servo_pulsewidth( self.SERVO_LEFTRIGHT_PIN, self.SERVO_CENTER[0] )
		elif hor>0:
			self.PG.set_servo_pulsewidth( self.SERVO_LEFTRIGHT_PIN, self.SERVO_CENTER[0]+int(self.SERVO_RANGE[0][1]*float(hor)/1000) )
		else:
			self.PG.set_servo_pulsewidth( self.SERVO_LEFTRIGHT_PIN, self.SERVO_CENTER[0]-int(self.SERVO_RANGE[0][0]*float(hor)/1000) )
		
	def servo_vertical(self, ver ): 
		if ver<-1000: ver=-1000
		if ver> 1000: ver= 1000
		if ver==0:
			self.PG.set_servo_pulsewidth( self.SERVO_UPDOWN_PIN, self.SERVO_CENTER[1] )
		elif ver>0:
			self.PG.set_servo_pulsewidth( self.SERVO_UPDOWN_PIN, self.SERVO_CENTER[1]+int(self.SERVO_RANGE[1][1]*float(ver)/1000) )
		else:
			self.PG.set_servo_pulsewidth( self.SERVO_UPDOWN_PIN, self.SERVO_CENTER[1]-int(self.SERVO_RANGE[1][0]*float(ver)/1000) )
	
	gpio_cleaned=False 
	def close(self ):
		self.daemon_running=False
		if not self.gpio_cleaned:
			self.gpio_cleaned=True
			self.ultrasonic_lock.acquire()
			GPIO.cleanup()
			self.ultrasonic_lock.release()
		
