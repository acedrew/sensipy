import json
import requests


class HutGripClient:

    """Provides api to push data to hutgrip cloud api"""

    appKey = "hgKeyHere"
    hostname = "http://api.hutgrip.com"

    def __init__(self, key=None):
        #self.logger = logging.getLogger('hg_client')
        #self.logger.setLevel(logging.DEBUG)
        if key is not None:
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
        #self.logger.debug(body)

        res = requests.put(
            self.hostname + "/dataFeeds/" + feedId, data=body,
            headers=self.getHeaders(body.__len__()))
        if res.status_code == 202:
            return "Sucess"
        else:
            return "Error sending data to API, status: " + str(res.status_code)
