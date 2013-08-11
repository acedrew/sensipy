from redis import Redis
from rq import Queue
from apscheduler.scheduler import Scheduler as apScheduler
import json
import requests


class scheduler():
    def __init__(self):
        self.queue = Queue(connection = Redis())
        self.configFile = 'config.json'

    def setup(self):
        self.loadconf()
        self.feeds = self.config['feeds']
        self.clientConf = self.config['client']
        #for feed in self.feeds:


    def loadConf(self):
        with open(self.configFile) as f:
            self.config = json.load(f)

    def run(self):
        return None

    def showConf(self):
        return json.dumps(self.config, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == "__main__":
    myScheduler = scheduler()
    myScheduler.loadConf()
    print myScheduler.showConf()

