import wificarwatchdog,time

wcdog=wificarwatchdog.WifiCarWatchdog()
wcdog.start_watchdog(21)

while(True):time.sleep(10)


