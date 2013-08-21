from redis import Redis
from datetime import datetime
from rq import Queue
from apscheduler.scheduler import Scheduler as apScheduler
from hutgrip import HutGripClient
import json
import logging


class scheduler():

    """This Class provide the main scheduler, it consumes the config
    and schedules the drivers to run for their respective feeds"""

    def __init__(self, loggingLevel=logging.ERROR):

        self.logger = logging.getLogger('hg_client')
        self.logger.setLevel(loggingLevel)
        fh = logging.FileHandler('error.log')
        fh.setLevel(logging.ERROR)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.hg = HutGripClient("NediLovesSeaFood")
        schedulerConfig = {
            'apscheduler.threadpool.max_threads': 2,
            'apscheduler.daemonic': False
        }
        self.queue = Queue(connection=Redis())
        self.scheduler = apScheduler(schedulerConfig)
        self.configFile = 'config.json'

    def start(self):

        """Runs all the initialization methods, then starts the
        scheduler in standalone (blocking) mode"""

        self.loadConf()
        self.loadDrivers()
        self.loadFeeds()
        self.runScheduler()
        self.scheduler.start()

    def stop(self):
        print "test"
        self.scheduler.shutdown()

    def loadDrivers(self):

        """Iterates through the Driver instances stored in the config,
        and loads corresponding instances into the driver dict"""

        self.drivers = {}
        for driver in self.config['drivers']:
            driverConf = self.config['drivers'][driver]
            baseClass = driverConf['baseClass']
            self.logger.debug("Loading: " + driver + /
                              " instance of: " + baseClass)
            driverArgs = driverConf['driver-config']
            self.drivers[driver] = {}
            try:
                tempModule = __import__('drivers.' + baseClass, /
                                        globals(), locals(), [baseClass], -1)
                self.drivers[driver]['driver'] = /
                getattr(tempModule, str(baseClass))(driverArgs)
            except Exception, e:
                self.logger.error("exception: " + e)
        return None

    def loadConf(self):

        """Retrieves config from file specified in __init__"""

        with open(self.configFile) as f:
            self.config = json.load(f)

    def printConf(self, args):
        print args
        print self.config

    def loadFeeds(self):

        """Sets up each feed in it's corresponding driver instance nice name
        """

        feeds = self.config['feeds']
        for feed in feeds:
            feedConf = self.config['feeds'][feed]
            feedConf['name'] = feed
            driver = feedConf['source']['driver']
            if not 'feeds' in self.drivers[driver['name']]:
                self.drivers[driver['name']]['feeds'] = []

            self.drivers[driver['name']]['feeds'].append(feedConf)

    def runScheduler(self):

        """Sets up base scheduler interval for each configured
        driver instance"""

        for driver in self.drivers:
            intervals = [int(self.drivers[driver]['feeds'][x]['interval']) /
                         for x in range(0, len(self.drivers[driver]['feeds']))]
            driverInterval = self.gcd(intervals)
            self.drivers[driver]['driverInterval'] = driverInterval
            self.logger.debug(self.drivers[driver]['feeds'])

            self.scheduler.add_interval_job(
                self.getDriverData, args=[self.drivers[driver]['feeds']],
                seconds=driverInterval)

    def getDriverData(self, feedSet):

        """Gets data from a single driver instance, on the intervals in
        each feeds config, data is put on the queue with all information
        needed to send to HG"""

        driverNiceName = feedSet[0]['source']['driver']['name']
        if not 'driverCounter' in self.drivers[driverNiceName]:
            self.drivers[driverNiceName]['driverCounter'] = /
            self.drivers[driverNiceName]['driverInterval']
        else:
            self.drivers[driverNiceName]['driverCounter'] += /
            self.drivers[driverNiceName]['driverInterval']
        for feed in feedSet:
            count = self.drivers[driverNiceName]['driverCounter']
            feedInterval = int(feed['interval'])
            if count % feedInterval == 0:
                feedId = feed['id']
                value = self.drivers[driverNiceName]['driver'].getData(feed)
                dt = datetime.utcnow()
                self.queue.enqueue(self.hg.addFeedData, feedId, value, dt)

    def gcd(self, nums):

        """Recursively computes Greatest Common Divisor for a list of
        numbers, used to compute the base scheduler interval for a
        given set of feed intervals"""

        if len(nums) == 1:
            return nums[0]
        if len(nums) == 0:
            return None
        if len(nums) >= 2:
            a = nums[-1:][0]
            b = nums[-2:-1][0]
            while b:
                a, b = b, a % b
            nums = nums[:-2]
            nums.append(a)
            return self.gcd(nums)

    def showConf(self):

        """Debug method to ensure config is loading correctly, and to
        pretty print a config to clean up one with miffed formatting"""

        return json.dumps(
            self.config, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":

    logging.basicConfig()
    myScheduler = scheduler()
    myScheduler.start()
