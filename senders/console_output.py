class Sender:
    """Each data sender implements a "Sender" class,
    providing a send_metric method which will push
    to whatever service that sender implements"""

    def send_metric(self, metricId, value, dateTime):
        print(metricId, str(value), str(dateTime))
        return True
