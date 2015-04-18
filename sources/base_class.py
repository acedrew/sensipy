import logging
from datetime import datetime


class base_source():

    """This class provides common functions for all sources"""

    def __init__(self, config):

        """Gets config from instantiation and provides it to whatever
        methods need it"""

        self.logger = logging.getLogger('sensipy')
        self.config = config
        self.data = {}
        self.ts = self.getTs()
        self.updateValues()

    def getTs(self):

        """returns UTC timestamp as int"""

        ts = int(datetime.utcnow().strftime('%s'))
        return ts
