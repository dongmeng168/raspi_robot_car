import time,wificar

wc=wificar.WifiCar()
wc.reset()
time.sleep(1)
for x in range(-1000,1000,250):
	wc.servo_horizontal(x)
	time.sleep(0.5)
wc.reset()
for x in range(-1000,1000,250):
	wc.servo_vertical(x)
	time.sleep(0.5)

