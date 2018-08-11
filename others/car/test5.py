import wificar,time

wc=wificar.WifiCar()

wc.feed_dog(21)
wc.forward(400)
time.sleep(1)
wc.stop()
wc.feed_dog(21)
wc.left_wheel(400)
time.sleep(1)
wc.stop()
wc.feed_dog(21)
wc.right_wheel(400)
time.sleep(1)
wc.stop()

