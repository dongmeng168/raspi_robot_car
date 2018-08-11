import wificar,time

wc=wificar.WifiCar()

for i in range(50):
  print wc.distance
  time.sleep(0.2)
  wc.feed_dog(21)



