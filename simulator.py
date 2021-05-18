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
    auth_config.read('./auth-config.ini')

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

    # generate independent streams
    ss = np.random.SeedSequence(12345)
    child_seeds = ss.spawn(sensors_number + 1)

    trendUpdater = TrendUpdaterThread(child_seeds[0], K)
    trendUpdater.start()

    for sensor_id in range(1, sensors_number + 1):
        rng_seed = child_seeds[sensor_id]
        user = User(sensor_id, "name", "name@example.com", rng_seed, AVG_EVENT_PERIOD, VAR_EVENT_PERIOD)
        generator = EventGenerator(user)
        EventSenderThread(rng_seed, generator, user.avg_event_period / K, GATEWAY_URL, auth).start()

    time.sleep(STOP / K)
    print("ending simulation...")
    eventing.stop = True
    trending.stop = True
