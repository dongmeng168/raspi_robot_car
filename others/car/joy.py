import pygame,time
pygame.init()

joy=pygame.joystick.Joystick(0)
joy.init()
print "AXES:",joy.get_numaxes()," BUTTONS:",joy.get_numbuttons()
while True:
	for event in pygame.event.get():
		print [joy.get_axis(i) for i in range(joy.get_numaxes())],[joy.get_button(i) for i in range(joy.get_numbuttons())],[joy.get_hat(i) for i in range(joy.get_numhats())]
		pass
	time.sleep(0.1)


