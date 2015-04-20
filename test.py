import unittest
from sources import systats


class SystemStatsTest(unittest.TestCase):

    def setUp(self):
        self.source = systats.systats({"myconfig": "test"})

    def testCpu(self):
        self.assertIs(type(
            self.source.getData({"source":
                                 {"driver": "systats"},
                                 "interval": "60",
                                 "multiplier": "1",
                                 "type": "cpuInfo",
                                 "param": "1min"})), float)
        self.assertIs(type(
            self.source.getData({"source":
                                 {"driver": "systats"},
                                 "interval": "60",
                                 "multiplier": "1",
                                 "type": "cpuInfo",
                                 "param": "5min"})), float)
        self.assertIs(type(
            self.source.getData({"source":
                                 {"driver": "systats"},
                                 "interval": "60",
                                 "multiplier": "1",
                                 "type": "cpuInfo",
                                 "param": "15min"})), float)

    def testMem(self):
        self.assertIs(type(
            self.source.getData({"source":
                                 {"driver": "systats"},
                                 "interval": "60",
                                 "multiplier": "1",
                                 "type": "memInfo",
                                 "param": "MemFree"})), float)

if __name__ == "__main__":
    unittest.main()
