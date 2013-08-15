from redis import Redis
from rq import Queue
from apscheduler.scheduler import Scheduler as apScheduler
import json
import requests
import importlib


class scheduler():
    def __init__(self):
        self.queue = Queue(connection = Redis())
        self.configFile = 'config.json'

    def setup(self):
        self.loadConf()
        #for feed in self.feeds:
    
    def loadDrivers(self):
        self.drivers = {}
        for driver in self.config['drivers']:
            driverConf = self.config['drivers'][driver]
            baseClass = driverConf['baseClass']
            driverArgs = driverConf['driver-config']
            try:
                tempModule = __import__('drivers.' + baseClass, globals(), locals(), [baseClass], -1)
                self.drivers[driver] =  getattr(tempModule, str(baseClass))(driverArgs)
            except Exception, e:
                print "tester"
                #print e
        return None 

    def loadConf(self):
        with open(self.configFile) as f:
            self.config = json.load(f)

    def run(self):
        return None

    def showConf(self):
        return json.dumps(self.config, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    myScheduler = scheduler()
    myScheduler.setup()
    myScheduler.loadDrivers()
    print myScheduler.config['feeds']['Tank 1 Controller Temp']
    print myScheduler.drivers['tank-controllers'].getData(myScheduler.config['feeds']['Tank 1 Controller Temp'])


