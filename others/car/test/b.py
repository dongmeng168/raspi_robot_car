import pigpio,time

PG=pigpio.pi()

PG.write(27,0)
PG.write(22,1)
PG.write(23,0)
PG.write(24,1)
PG.set_PWM_frequency(18,400)
PG.set_PWM_frequency(25,400)
PG.set_PWM_range(18,1000)
PG.set_PWM_range(25,1000)
PG.set_PWM_dutycycle(18,350)
PG.set_PWM_dutycycle(25,350)

time.sleep(2)
PG.set_PWM_dutycycle(18,0)
PG.set_PWM_dutycycle(25,0)



