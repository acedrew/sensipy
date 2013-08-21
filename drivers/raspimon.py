from datetime import datetime
from subprocess import check_output
import logging

class raspimon():
    """This driver provides system data for the raspberry pi
    used commonly as a gateway for the hutgrip platform"""


    def __init__(self, config):

        """Gets config from instantiation and provides it to whatever methods need it"""

        self.logger = logging.getLogger('hg_client')
        self.config = config
        self.data = {}
        self.ts = self.getTs()
        self.updateValues()
        

    def getTs(self):
        ts = int(datetime.utcnow().strftime('%s'))
        return ts

    def getMemInfo(self):
        if not 'memInfo' in self.data:
            self.data['memInfo'] = {}
        try:
            rawInfo = check_output(["cat", "/proc/meminfo"])
            for line in rawInfo.splitlines():
                pair = line[:-3].replace(" ", "").split(':')
                self.data['memInfo'][pair[0]] = int(pair[1])
        except:
            self.logger.error('retrieval of meminfo failed')


    def getCpuInfo(self):
        if not 'cpuInfo' in self.data :
            self.data['cpuInfo'] = {}
        try:
            rawInfo = check_output(["cat", "/proc/loadavg"])
            vals = rawInfo.splitlines()[0].split()
            self.data['cpuInfo']['1min'] = float(vals[0])
            self.data['cpuInfo']['5min'] = float(vals[1])
            self.data['cpuInfo']['15min'] = float(vals[2])
        except:
            self.logger.error('retrieval of cpu loadavg failed')



    def updateValues(self):
        self.getCpuInfo()
        self.getMemInfo()



    def getData(self, feed):
        driver = feed['source']['driver']
        now = self.getTs()
        if (now - self.ts) > (int(feed['interval']) / 2):
            self.updateValues()
            self.ts = self.getTs()
        multiplier = float(feed['multiplier'])
        data = float(self.data[driver['type']][driver['param']]) * multiplier
        return data
      
