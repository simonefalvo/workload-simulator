import sys
import configparser
import time

import numpy as np

import eventing
import trending
from eventing import EventGenerator
from eventing import EventSenderThread
from model import User
from trending import TrendUpdaterThread

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: python simulator.py <number of sensors>")
        exit()

    config = configparser.ConfigParser()
    auth_config = configparser.ConfigParser()
    config.read('./config.ini')
    auth_config.read('./auth_config.ini')

    K = config.getfloat('SIMULATOR', 'K')  # time compression factor
    STOP = config.getint('SIMULATOR', 'STOP')
    GATEWAY_URL = config.get('NETWORK', 'GATEWAY')
    AVG_EVENT_PERIOD = config.getint('USER', 'AVG_EVENT_PERIOD')
    VAR_EVENT_PERIOD = config.getint('USER', 'VAR_EVENT_PERIOD')
    print("Time compression factor: K=", K, file=sys.stderr)
    print("Simulation duration: %d seconds" % STOP, file=sys.stderr)
    print("Gateway url:", GATEWAY_URL, file=sys.stderr)
    print("Average user event period: %d seconds" % AVG_EVENT_PERIOD, file=sys.stderr)
    print("User event period variance: %d seconds" % VAR_EVENT_PERIOD, file=sys.stderr)

    USERNAME = auth_config.get('OPENFAAS', 'USERNAME')
    PASSWORD = auth_config.get('OPENFAAS', 'PASSWORD')
    auth = (USERNAME, PASSWORD)

    sensors_number = int(sys.argv[1])
    print("Number of sensors:", sensors_number, file=sys.stderr)

    np.random.seed(12345)

    trendUpdater = TrendUpdaterThread()
    trendUpdater.start()

    for sensor_id in range(1, sensors_number + 1):
        user = User(sensor_id, "name", "name@example.com", AVG_EVENT_PERIOD, VAR_EVENT_PERIOD)
        generator = EventGenerator(user)
        EventSenderThread(generator, K * user.avg_event_period, GATEWAY_URL, auth).start()

    time.sleep(STOP)
    print("ending simulation...")
    eventing.stop = True
    trending.stop = True
