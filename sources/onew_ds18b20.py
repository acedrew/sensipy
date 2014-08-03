import os.path
from datetime import datetime
import logging


class onew_ds18b20():

    """Driver class for the one wire DS18B20 temperature sensor"""

    def __init__(self, config):

        """Gets config from instantiation and provides it to whatever
        methods need it"""

        self.logger = logging.getLogger('hg_client')
        self.config = config
        self.data = {}
        self.ts = self.getTs()

    def getTs(self):

        """returns UTC timestamp as int"""

        ts = int(datetime.utcnow().strftime('%s'))
        return ts

    def getData(self, feed):

        """Gets temp for a single feed from one wire filesystem"""

        driver = feed['source']['driver']
        sensorpath = self.config["basepath"] + driver['unitId'] + "/w1_slave"
        if not feed['id'] in self.data:
            self.data[feed['id']] = {}
        try:
            if not os.path.exists(sensorpath):
                raise Exception('sensor does not exist')
            with open(sensorpath) as fd:
                data = fd.read()
                data.replace("\n", "")

                if data.find("YES") > -1:
                    v = data[-6:]
                    data = float(v) * float(feed['multiplier'])
                    #self.logger.error(str(data) + " is the value being reported")
                    return data

        except Exception, e:
            self.logger.error(
                'retrieval of temp for sensor %s failed, exceptions %s' % (
                    feed['name'], e))
