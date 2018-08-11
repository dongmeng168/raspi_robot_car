#!/usr/bin/python
#-!- coding: utf-8 -!-
""" WiFi Car Watchdog use invisible GPIO pin to check main thread is running. """
import pigpio,thread,time
import wificar

class WifiCarWatchdog(wificar.WifiCar):
	def __init__(self,address=None ):
		if address:
			self.PG=pigpio.pi( address )
		else:
			self.PG=pigpio.pi()
		
	def start_watchdog(self, pin ):
		""" watchdog check 'pin' every 0.5 seconds, if no change on pin more than 2.5 seconds. It will shut off the L298N to prevent car damage. """
		thread.start_new_thread( self.check_watchdog, ( pin, ) )
	
	def check_watchdog(self, pin ):
		watchdog_counter=0
		while True:
			if self.PG.wait_for_edge( pin, pigpio.EITHER_EDGE, 0.5 ):
				watchdog_counter=0
				time.sleep(0.25)
			else:
				watchdog_counter+=1
				if watchdog_counter>5: # Watch dog stopped.
					print "Watch dog activated!",time.ctime()
					self.stop()
					self.inverse_led('red')
	
