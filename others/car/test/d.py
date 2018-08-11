import pigpio,time

PG=pigpio.pi()
PG.write(4,0)
time.sleep(0.00001)
PG.write(4,1)
start=time.time()
while PG.read(17)==0:
	start=time.time()

while PG.read(17)==1:
	end=time.time()
elapsed = stop-start
distance = elapsed * 34000
distance = distance / 2
print distance
