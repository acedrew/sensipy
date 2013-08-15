from redis import Redis
from datetime import datetime
from rq import Queue
from time import sleep
from apscheduler.scheduler import Scheduler as apScheduler
import json
import requests
import importlib
import logging


class scheduler():
    def __init__(self):
        schedulerConfig = {'threadpool.max_threads': 1}
        self.queue = Queue(connection = Redis())
        self.scheduler = apScheduler(schedulerConfig)
        self.scheduler.start()
        self.configFile = 'config.json'

    def setup(self):
        self.loadConf()
        #for feed in self.feeds:
    
    def loadDrivers(self):

        """Iterates through the Driver instances stored in the config,
        and loads corresponding instances into the driver dict"""
        
        self.drivers = {}
        for driver in self.config['drivers']:
            print driver
            driverConf = self.config['drivers'][driver]
            baseClass = driverConf['baseClass']
            driverArgs = driverConf['driver-config']
            self.drivers[driver] = {}
            try:
                tempModule = __import__('drivers.' + baseClass, globals(), locals(), [baseClass], -1)
                self.drivers[driver]['driver'] =  getattr(tempModule, str(baseClass))(driverArgs)
            except Exception, e:
                print "exception"
                print e
        return None 

    def loadConf(self):
        with open(self.configFile) as f:
            self.config = json.load(f)
            
    def printConf(self, args):
        print args
        print self.config


    def loadFeeds(self):
        feeds = self.config['feeds']
        for feed in feeds:
            feedConf = self.config['feeds'][feed]
            driver = feedConf['source']['driver']
            if not 'feeds' in self.drivers[driver['name']]:
                self.drivers[driver['name']]['feeds'] = []

            self.drivers[driver['name']]['feeds'].append(feedConf)

            #self.scheduler.add_interval_job(self.printConf, args=['print some stuff'], seconds=20)

            #self.scheduler.add_interval_job(self.drivers[driver['name']].getData, args=[feedConf], seconds=10)

    def runScheduler(self):
        for driver in self.drivers:
            intervals = [int(self.drivers[driver]['feeds'][x]['interval']) for x in range(0,len(self.drivers[driver]['feeds']))]
            driverInterval = self.gcd(intervals)
            self.drivers[driver]['driverInterval'] = driverInterval
            print driverInterval
            print driver

            self.scheduler.add_interval_job(self.getDriverData, args=[self.drivers[driver]['feeds']], seconds=driverInterval)


    def getDriverData(self, feedSet):
        driverNiceName = feedSet[0]['source']['driver']['name']
        if not 'driverCounter' in self.drivers[driverNiceName]:
            self.drivers[driverNiceName]['driverCounter'] = 0
        else:
            self.drivers[driverNiceName]['driverCounter'] += self.drivers[driverNiceName]['driverInterval']
        for feed in feedSet:
            count = self.drivers[driverNiceName]['driverCounter']
            feedInterval = int(feed['interval'])
            if count % feedInterval == 0:
                print self.drivers[feed['source']['driver']['name']]['driver'].getData(feed)
            
    def gcd(self, nums):
        if len(nums) == 1:
            return nums[0]
        if len(nums) == 0:
            return None
        if len(nums) >= 2:
            a = nums[-1:][0]
            b = nums[-2:-1][0]
            while b:
                a, b = b, a%b
            nums = nums[:-2]
            nums.append(a)
            return self.gcd(nums)



    def run(self):
        return None

    def showConf(self):
        return json.dumps(self.config, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":

    logging.basicConfig()
    myScheduler = scheduler()
    myScheduler.setup()
    #while True:
    #    sleep(1)
    myScheduler.loadDrivers()
    myScheduler.loadFeeds()
    myScheduler.runScheduler()
    while True:
        sleep(1)


