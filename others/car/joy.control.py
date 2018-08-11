#!/usr/bin/python
#-!- coding: utf-8 -!-

import time,wificar,sys,pygame,traceback


pygame.init()

if pygame.joystick.get_count()==0:
	print "Could not find Joystick!"
	sys.exit()
	
joy=pygame.joystick.Joystick(0)
joy.init()

car=wificar.WifiCar()
car.reset()

print 'Car online ...'

try:
	while True:
		for event in pygame.event.get(): # just read the event.
			pass 
		
		axes= [joy.get_axis(i) for i in range(joy.get_numaxes())]
		button=[joy.get_button(i) for i in range(joy.get_numbuttons())]
		hat=joy.get_hat(0)
		
		# if button 7 pressed, flash blue.
		if button[6]:
			car.led('blue',True)
		else:
			car.led('blue',False)
		
		car.forward( -axes[1]*(700+button[6]*300) ,axes[0]*900 )
		car.servo_horizontal( axes[2]*1000 )
		car.servo_vertical  ( axes[3]*1000 )
		
		if hat[0]!=0 or hat[1]!=0:
			if hat[1]==-1:
				car.forward(-700, 0)
			elif hat[1]==1:
				car.forward(700, 0 )
			elif hat[0]==-1:
				car.forward(0,-700)
			elif hat[0]==1:
				car.forward(0,700)
		
		time.sleep(0.1)
except:
	car.close()
	time.sleep(0.1)
	traceback.print_exc()
			