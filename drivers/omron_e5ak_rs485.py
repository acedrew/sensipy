import serial
from time import sleep
from datetime import datetime
class omron_e5ak_rs485():

  """Driver class for Omron E5AK loop controller, with RS-485 communications module"""

  def __init__(self, config):

    """Gets config from instantiation and provides it to whatever methods need it"""

    self.config = config
    self.openConnection()

  def getData(self, feed):
    point = feed['source']['driver']
    if(point['type'] == "parameter"):
      data = self.getParameter(point['unitId'], point['address'])
    return data
  
  def openConnection(self):
  
    """Creates a serial connection object according to the setting stored in the
    config.json file"""
  
    port = self.config["serialPortSettings"]["port"]
    baud = self.config["serialPortSettings"]["baudRate"]
  
    print "Opening connection: \n\tport: {0}\n\tbaud rate: {1}".format(
      port, baud)
  
    self.con = serial.Serial(port, baud, parity=serial.PARITY_EVEN, timeout=0.5 )
    return None
  
  def loadFeeds(self):
    feeds = self.config['feeds']
    for feed in feeds:
      print feed
      feedConf = self.config['feeds'][feed]
      driver = feedConf['source']['driver']
      #self.scheduler.add_interval_job(self.printConf, args=['print some stuff'], seconds=20)

            
  def calcCRC(self, msg):
  
    """Calculates CRC or Frames Check sequence by doing a bitwise xor on the ordinal char number for each char in the command sequence"""
  
    fcs = 0
    for ch in msg:
      fcs = fcs ^ ord(ch)
    return '{:x}'.format(fcs)
  
  def checkCRC(self, msg):
  
    """Returns True if crc on received message is correct"""
  
    return self.calcCRC(msg[:-4]) == msg[-4:-2]
  
  def sendCommand(self, device, cmd, parameter, value = "0000"):
  
    """This function assembles the command string, and sends it via the passed
    serial connection"""
  
    command = "@{0}{1}{2}{3}".format(device, cmd, parameter, value)
    command += self.calcCRC(command) + "*\r\n"
    print "Command: ", command
    self.con.write(command)
    sleep(0.1)
    
    if self.con.inWaiting() == 0:
      print "No answer..."
      return None
    
    #sleep(0.5)
    #this was what was causing most of the issues, returing a multiline string.
    #called splitlines, and return the second line.
    answer = self.con.readlines()[1]
    print "Answer: ", answer, 
    if not self.checkCRC(answer):
      print "Incorrect CRC ", answer
      return None
  
    if (answer[-2:-1] != "*"):
      print "Invalid message received...", answer
      return None
  
    if (answer[6:8] != "00"):
      print "Invalid End Code received, please check documentation...", answer
      return None
  
    return answer
  
  #@01100000070*
  def getParameter(self, device, parameter):
  
    """Gets raw parameter"""
  
    result = self.sendCommand(device, "1",  parameter, "0000")
    print result  
    if result == None:
      return None
      
    return int(result[6:-4])
  
  def setParameter(self, device, parameter, value):
  
    """sets raw parameter"""
  
    result = sendCommand(device, "2", parameter, value)
    
    if result == None:
      return None
    return result
  
  def setSpecial(self, device, command, instruction):
  
    """Sets Special parameters"""
  
    result = sendCommand(device, "3", command, instruction)
    
    if result == None:
      return None
    return result
  
