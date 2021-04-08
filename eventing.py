from threading import Thread
import json
import time
import requests
import numpy as np

import trending


class EventSenderThread(Thread):

    def __init__(self, event_generator, avg_period, url, auth):
        Thread.__init__(self)
        self.__event_generator = event_generator
        self.__avg_period = avg_period
        self.__url = url
        self.__auth = auth

    @property
    def event_generator(self):
        return self.__event_generator

    @property
    def avg_period(self):
        return self.__avg_period

    @property
    def url(self):
        return self.__url

    @property
    def auth(self):
        return self.__auth

    def run(self):
        # random start (at least 30 seconds of time range)
        start_delay = np.random.uniform(0, max(30.0, self.avg_period))
        time.sleep(start_delay)

        while True:
            next_avg_period = self.avg_period / (1 + trending.trend)
            sleep_time = np.random.exponential(scale=next_avg_period)
            time.sleep(sleep_time)
            event = self.event_generator.next()
            self.send_event(event)

    def send_event(self, event):
        headers = {'Content-type': 'application/json'}
        response = requests.post(url=self.url, data=event, auth=self.auth, headers=headers)
        print("{}: [{} {}] {}".format(
            self.event_generator.user.sensor_id,
            response.status_code,
            response.reason,
            response.text))


class EventGenerator:

    def __init__(self, user):
        self.__user = user

    @property
    def user(self):
        return self.__user

    def build_event(self):
        timestamp = time.time()
        event = {
            "data": "test",
            "timestamp": timestamp,
            "sensor_id": self.user.sensor_id
        }
        json_event = json.dumps(event, indent=2)
        return json_event

    def next(self):
        return self.build_event()
