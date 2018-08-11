import wificar
import time

wc=wificar.WifiCar()
wc.led('red')
time.sleep(1)
wc.led('blue')
time.sleep(1)
wc.led('green')
time.sleep(1)

for i in range(10):
	wc.inverse_led('green')
	time.sleep(1)

wc.led('red',False)
wc.led('green',False)
wc.led('blue',False)

