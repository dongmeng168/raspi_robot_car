#!/usr/bin/python
#-!- coding: utf-8 -!-

import time,wificar,sys,thread
import curses,traceback

wc=wificar.WifiCar()
cu=curses.initscr()
curses.noecho()

# if key pressed, update this to timer.
key_timer=time.time()

# If no key pressed more than 0.5 second, stop the car.
def check_key_pressed():
	global key_timer
	global speed
	global direction
	while True:
		if time.time()-key_timer>0.5:
			wc.stop()
			speed=0
			direction=0
		time.sleep(0.05)

# Start key up check thread.
thread.start_new_thread( check_key_pressed, () ) 

speed=0
direction=0
MOVE_SPEED=800
ROTATE_SPEED=800
servo_hor=0
servo_ver=0
esckey1=False
esckey2=False

try:
	while 1:
		updated=True
		key=cu.getch() # read char.
		if key==27: # Escape key.
			esckey1=True
			updated=False
		elif key==91 and esckey1: 
			esckey2=True
			updated=False
		elif key==curses.KEY_UP or esckey1 and esckey2 and key==65:
			speed=MOVE_SPEED
			direction=0
		elif key==curses.KEY_DOWN or esckey1 and esckey2 and key==66:
			speed=-MOVE_SPEED
			direction=0
		elif key==curses.KEY_LEFT or esckey1 and esckey2 and key==67:
			direction=ROTATE_SPEED
		elif key==curses.KEY_RIGHT or esckey1 and esckey2 and key==68:
			direction=-ROTATE_SPEED
		elif key in [ord(' ')]:
			speed=0
			direction=0
		elif key in [ord('A'),ord('a')]:
			servo_hor-=10
		elif key in [ord('D'),ord('d')]:
			servo_hor+=10
		elif key in [ord('W'),ord('w')]:
			servo_ver-=10
		elif key in [ord('S'),ord('s')]:
			servo_ver+=10
		elif key in [ord('Z'),ord('z')]:
			servo_hor=0
			servo_ver=0
		else:
			updated=False
		if updated: 
			key_timer=time.time()
			esckey1=False
			esckey2=False
		wc.forward( speed, direction )
		wc.servo_horizontal( servo_hor )
		wc.servo_vertical( servo_ver )
except:
	curses.echo()
	curses.endwin()
	wc.close()
	time.sleep(0.1)
	traceback.print_exc()
	