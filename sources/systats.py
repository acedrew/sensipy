from subprocess import check_output
from sources import base_class


class systats(base_class.base_source):

    """This source provides system data for the raspberry pi
    used as a gateway"""

    def __init__(self, config):
        super().__init__(config)

        """Gets config from instantiation and provides it to whatever
        methods need it"""

    def getMemInfo(self):

        """Collects memory useage data from /proc/meminfo, populates
        a dict with the data"""

        if 'memInfo' not in self.data:
            self.data['memInfo'] = {}
        try:
            rawInfo = check_output(["cat", "/proc/meminfo"])
            for line in rawInfo.splitlines():
                lineSplit = line.decode("utf-8")[:-3].split()
                if len(lineSplit) > 1:
                    pair = "".join(lineSplit).split(":")
                self.data['memInfo'][pair[0]] = int(pair[1])
        except:
            self.logger.error('retrieval of meminfo failed')

    def getCpuInfo(self):

        """Collects CPU load data from /proc/loadavg, populates the data
        dict with key value pairs"""

        if 'cpuInfo' not in self.data:
            self.data['cpuInfo'] = {}
        try:
            rawInfo = check_output(["cat", "/proc/loadavg"])
            vals = rawInfo.splitlines()[0].split()
            self.data['cpuInfo']['1min'] = float(vals[0])
            self.data['cpuInfo']['5min'] = float(vals[1])
            self.data['cpuInfo']['15min'] = float(vals[2])
        except:
            self.logger.error('retrieval of cpu loadavg failed')

    def getCpuTemp(self):

        """Collects CPU load data from /proc/loadavg, populates the data
        dict with key value pairs"""

        if 'cpuInfo' not in self.data:
            self.data['cpuInfo'] = {}
        try:
            rawInfo = check_output(["cat",
                                    "/sys/class/thermal/thermal_zone0/temp"])
            vals = rawInfo
            self.data['cpuInfo']['temp'] = float(vals)
        except:
            self.logger.error('retrieval of cpu temp failed')

    def updateValues(self):

        """Calls all data collection methods, to update values in
        self.data dict"""

        for typeName in self.typesInitted:
            typeName = typeName[0].upper() + typeName[1:]
            getattr(self, "get" + typeName)()
        """self.getCpuInfo()
        self.getMemInfo()
        self.getCpuTemp()"""

    def getData(self, feed):

        """Returns value for given feed"""

        if feed['type'] not in self.typesInitted:
            self.typesInitted.append(feed['type'])
        now = self.getTs()
        if (now - self.ts) > (int(feed['interval']) / 2):
            self.updateValues()
            self.ts = now
        multiplier = float(feed['multiplier'])
        result = float(self.data[feed["type"]][feed["param"]]) * multiplier
        print(result)
        return result
