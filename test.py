from sources import raspimon
test = raspimon.raspimon({"myconfig":"test"})
print(test.getData({"source":{"driver": "raspimon"},"interval": "60", "multiplier": "1", "type": "cpuInfo", "param": "1min"}))
