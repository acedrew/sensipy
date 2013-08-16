import json
import requests
from datetime import datetime

class HutGripClient:
  appKey = "hgKeyHere"
  hostname = "http://api.hutgrip.com"

  def __init__(self, key=None):
    if key != None:
      self.appKey = key

  def getHeaders(self, dataLength):
    headers = {
      "content-type": "application/json",
      "hgKey": self.appKey,
      "content-Length": dataLength}

    return headers

  def addFeedData(self, feedId, value, dateTime):
    data = {
      "date": dateTime.isoformat() + "Z", 
      "value": value}

    body = json.dumps(data)
    print body

    res = requests.put(self.hostname+"/dataFeeds/" + feedId, data=body, headers=self.getHeaders(body.__len__()))
    return "Sucess"
