import logging
import socket
from datetime import datetime


class omega_weather:

    """This driver provides temperature and humidity data
    for the Omega/Newport Instruments iTHX T3"""

    def __init__(self, config):

        """Gets config from instantiation and provides it to whatever
        methods need it"""

        self.logger = logging.getLogger('hg_client')
        self.config = config
        self.connect()
        self.ts = self.getTs()
        self.data = {}
        self.updateValues()

    def getTs(self):

        """returns UTC timestamp as int"""

        ts = int(datetime.utcnow().strftime('%s'))
        return ts

    def connect(self):

        """Sets up TCP connection using config"""

        try:
            TCP_IP = self.config["host"]
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((TCP_IP, 2000))
        except Exception, e:
            self.logger.debug("Error creating socket connection " + str(e))

    def updateValues(self):

        """Calls all data collection methods, to update values in
        self.data dict"""

        validparams = {"HA", "TA", "DA"}
        self.data = {}
        while not validparams.issubset(set(self.data.keys())):
            raw = self.socket.recv(256)
            self.data[raw[:2]] = raw[2:].strip().strip("C%\r")

    def getData(self, feed):

        """Returns value for given feed"""

        driver = feed['source']['driver']
        now = self.getTs()
        if (now - self.ts) > (int(feed['interval']) / 2):
            self.updateValues()
            self.ts = self.getTs()
        multiplier = float(feed['multiplier'])
        data = float(self.data[driver['param']]) * multiplier
        return data
