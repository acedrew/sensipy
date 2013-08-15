import serial
import json
from hutgrip import HutGripClient
from time import sleep
from datetime import datetime
class omron_e5ak_rs485():
  def __init__(self, config):
    self.config = config
    print config
    return None

  
  def openConnection(self):
  
    """Creates a serial connection object according to the setting stored in the
    config.json file"""
  
    port = config["serialPortSettings"]["port"]
    baud = config["serialPortSettings"]["baudRate"]
  
    print "Opening connection: \n\tport: {0}\n\tbaud rate: {1}".format(
      port, baud)
  
    return serial.Serial(port, baud, parity=serial.PARITY_EVEN )
  
  def calcCRC(self, msg):
  
    """Calculates CRC or Frames Check sequence by doing a bitwise xor on the ordinal char number for each char in the command sequence"""
  
    fcs = 0
    for ch in msg:
      fcs = fcs ^ ord(ch)
    print fcs
    print ("00" + '{:x}'.format(fcs))[-2:]
    return '{:x}'.format(fcs)
  
  def checkCRC(self, msg):
  
    """Returns True if crc on received message is correct"""
  
    return calcCRC(msg[:-3]) == msg[-3:-1]
  
  def sendCommand(self, device, cmd, parameter, value = "0000"):
  
    """This function assembles the command string, and sends it via the passed
    serial connection"""
  
    command = "@{0}{1}{2}{3}".format(device, cmd, parameter, value)
    print command
    command += calcCRC(command) + "*\r\n"
    print "Command: ", command
    serial.write(command)
    sleep(0.1)
    
    if serial.inWaiting() == 0:
      print "No answer..."
      return None
    
    #sleep(0.5)
    #this was what was causing most of the issues, returing a multiline string.
    #called splitlines, and return the second line.
    answer = serial.read(serial.inWaiting()).splitlines()[1]
    print "Answer: ", answer, 
    if not checkCRC(answer):
      print "Incorrect CRC ", answer
      return None
  
    if (answer[-1:] != "*"):
      print "Invalid message received...", answer
      return None
  
    if (answer[6:8] != "00"):
      print "Invalid End Code received, please check documentation...", answer
      return None
  
    return answer[7:][:-3]
  
  #@01100000070*
  def getParameter(self, device, parameter):
  
    """Gets raw parameter"""
  
    result = sendCommand(device, "1",  parameter, "0000")
    print result  
    if result == None:
      return None
      
    return int(result)
  
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
  
#while True:
#    com = openConnection()
#    setSpecial(com, "01", "02", "0001")
#    setSpecial(com, "01", "00", "0000")
#    setParameter(com, "01", "01", "0030")
#    com.close()
#    sleep(600)
if __name__ == "__main__":
  com = None
  with open("./dixieConnectorConfig.json") as configFile:
  	config = json.load(configFile)
  
  hg = HutGripClient("NediLovesSeaFood")
  while True:
  
    try:
      if com == None:
        com = openConnection()
        print com.getSettingsDict()
      for controller in config['controllers']:
          dt = datetime.utcnow()
          for sensor in controller['sensors']:
              value = getParameter(com, controller['address'], sensor['parameter'])
              print value
              resp = hg.addFeedData(sensor['feedId'], (value * float(sensor['multiplier'])), dt)
  
    except Exception, e:
        print e
        sleep(5)
        if com != None:
          com.close()
          com = None
  
    sleep(10) 
