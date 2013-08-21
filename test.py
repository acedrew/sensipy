from drivers import raspimon
test = raspimon.raspimon({"myconfig":"test"})
print test.getData({"interval": "60", "multiplier": "1", "type": "cpuInfo", "param": "1min"})  
