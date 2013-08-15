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
                self.drivers[driver]['intervals'] = {}
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
            if not (str(feedConf['frequency']) in self.drivers[driver['name']]['intervals']):
                self.drivers[driver['name']]['intervals'][str(feedConf['frequency'])] = []
            self.drivers[driver['name']]['intervals'][str(feedConf['frequency'])].append(feedConf)

            #self.scheduler.add_interval_job(self.printConf, args=['print some stuff'], seconds=20)

            #self.scheduler.add_interval_job(self.drivers[driver['name']].getData, args=[feedConf], seconds=10)

    def runScheduler(self):
        for driver in self.drivers:
            print driver
            for interval in self.drivers[driver]['intervals']:
                print int(interval)

                self.scheduler.add_interval_job(self.getDriverData, args=[self.drivers[driver]['intervals'][interval]], seconds=int(interval))


    def getDriverData(self, feedSet):
        for feed in feedSet:
            print self.drivers[feed['source']['driver']['name']]['driver'].getData(feed)
            


    def run(self):
        return None

    def showConf(self):
        return json.dumps(self.config, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    logging.basicConfig()
    myScheduler = scheduler()
    myScheduler.setup()
    myScheduler.loadDrivers()
    myScheduler.loadFeeds()
    myScheduler.runScheduler()
    while True:
        sleep(1)


