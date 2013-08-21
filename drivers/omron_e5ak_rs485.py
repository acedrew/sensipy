import serial
from time import sleep
import logging


class omron_e5ak_rs485():

    """Driver class for Omron E5AK loop controller, with RS-485
    communications module"""

    def __init__(self, config):

        """Gets config from instantiation and provides it to whatever
        methods need it"""

        self.logger = logging.getLogger('hg_client')
        self.config = config
        self.openConnection()

    def getData(self, feed):
        multiplier = float(feed['multiplier'])
        point = feed['source']['driver']
        if(point['type'] == "parameter"):
            data = int(
                self.getParameter(point['unitId'], point['address'])) * /
            multiplier
        return data

    def openConnection(self):

        """Creates a serial connection object according to the setting
        stored in the config.json file"""

        port = self.config["serialPortSettings"]["port"]
        baud = self.config["serialPortSettings"]["baudRate"]

        self.logger.debug("Opening connection:" + /
                          "\n\tport: {0}\n\tbaud rate: {1}".format(
                              port, baud))

        self.con = serial.Serial(
            port, baud, parity=serial.PARITY_EVEN, timeout=0.5)
        return None

    def calcCRC(self, msg):

        """Calculates CRC or Frames Check sequence by doing a bitwise
        xor on the ordinal char number for each char in the command
        sequence"""

        fcs = 0
        for ch in msg:
            fcs = fcs ^ ord(ch)
        return '{:x}'.format(fcs).lower()

    def checkCRC(self, msg):

        """Returns True if crc on received message is correct"""

        return self.calcCRC(msg[:-4]) == msg[-4:-2].lower()

    def sendCommand(self, device, cmd, parameter, value="0000"):

        """This function assembles the command string, and sends it
        via the passed serial connection"""

        command = "@{0}{1}{2}{3}".format(device, cmd, parameter, value)
        command += self.calcCRC(command) + "*\r\n"
        self.logger.debug("Command: " + command)
        self.con.write(command)
        sleep(0.1)

        if self.con.inWaiting() == 0:
            self.logger.error("No answer...")
            return None

        #sleep(0.5)
        #this was what was causing most of the issues, returning a
        #multiline string.
        #called splitlines, and return the second line.

        answer = self.con.readlines()[1]
        self.logger.debug("Answer: " + answer)
        if not self.checkCRC(answer):
            self.logger.error("Incorrect CRC " + answer)
            return None

        if (answer[-2:-1] != "*"):
            self.logger.error("Invalid message received..." + answer)
            return None

        if (answer[6:8] != "00"):
            self.logger.error("Invalid End Code received, please check" + /
                              "documentation..." + answer)
            return None

        return answer

    #@01100000070*
    def getParameter(self, device, parameter):

        """Gets raw parameter"""

        result = self.sendCommand(device, "1",    parameter, "0000")
        if result is None:
            return None

        return int(result[6:-4])

    def setParameter(self, device, parameter, value):

        """sets raw parameter"""

        result = sendCommand(device, "2", parameter, value)

        if result is None:
            return None
        return result

    def setSpecial(self, device, command, instruction):

        """Sets Special parameters"""

        result = sendCommand(device, "3", command, instruction)

        if result is None:
            return None
        return result
