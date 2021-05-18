import configparser
import math
import time
import numpy as np
from threading import Thread

trend = 0
stop = False


def _update_trend_exp(elapsed, start, target, conv_rate):
    global trend
    trend = target + (start - target) * math.exp(- conv_rate * elapsed)


def _update_trend_lin(elapsed, conv_rate):
    global trend
    trend = conv_rate * elapsed


class TrendUpdaterThread(Thread):

    def __init__(self, rng_seed, compression):
        Thread.__init__(self)
        config = configparser.ConfigParser()
        config.read('./config.ini')
        self._rng = np.random.default_rng(rng_seed)
        self._compression = compression
        self._avg_conv_rate = config.getfloat('TREND', 'AVG_CONV_RATE')
        self._tick = config.getfloat('TREND', 'TICK')  # trend update period
        self._min_regular_trend = config.getfloat('TREND', 'MIN_REGULAR_TREND') - 1
        self._max_regular_trend = config.getfloat('TREND', 'MAX_REGULAR_TREND') - 1
        self._min_spike_trend = config.getfloat('TREND', 'MIN_SPIKE_TREND') - 1
        self._max_spike_trend = config.getfloat('TREND', 'MAX_SPIKE_TREND') - 1
        self._avg_spike_period = config.getfloat('TREND', 'AVG_SPIKE_PERIOD')
        min_negative_factor = config.getfloat('TREND', 'MIN_NEGATIVE_SPIKE_TREND')
        max_negative_factor = config.getfloat('TREND', 'MAX_NEGATIVE_SPIKE_TREND')
        self._min_negative_trend = (min_negative_factor - 1) / min_negative_factor
        self._max_negative_trend = (max_negative_factor - 1) / max_negative_factor
        self._negative_spike_prob = config.getfloat('TREND', 'NEGATIVE_SPIKE_PROB')
        self._tolerance = config.getfloat('TREND', 'TOLERANCE')

    @property
    def rng(self):
        return self._rng
        
    @property
    def compression(self):
        return self._compression

    @property
    def avg_conv_rate(self):
        return self._avg_conv_rate

    @property
    def min_regular_trend(self):
        return self._min_regular_trend

    @property
    def max_regular_trend(self):
        return self._max_regular_trend

    @property
    def min_spike_trend(self):
        return self._min_spike_trend

    @property
    def max_spike_trend(self):
        return self._max_spike_trend

    @property
    def avg_spike_period(self):
        return self._avg_spike_period

    @property
    def negative_spike_prob(self):
        return self._negative_spike_prob

    @property
    def tick(self):
        return self._tick

    @property
    def tolerance(self):
        return self._tolerance

    def run(self):

        update_period = self.tick / self.compression
        start_trend = 0
        target_trend = self.rng.uniform(self._min_regular_trend, self._max_regular_trend)
        conv_rate = self.rng.normal(self.avg_conv_rate, self._avg_conv_rate / 4)
        print("new target: {}, conv_rate: {}".format(target_trend, conv_rate))
        spike_time = self.rng.exponential(self.avg_spike_period)
        print("next spike will trigger in {} seconds".format(spike_time))
        start = time.time()

        while not stop:

            elapsed = (time.time() - start) * self.compression
#            _update_trend_lin(elapsed, conv_rate)
            _update_trend_exp(elapsed, start_trend, target_trend, conv_rate)

            if elapsed >= spike_time:
                print("spike started")
                start_trend = trend
                if self.rng.random() <= self.negative_spike_prob:
                    target_trend = - self.rng.uniform(self._min_negative_trend, self._max_negative_trend)
                else:
                    target_trend = self.rng.uniform(self.min_spike_trend, self.max_spike_trend)
                conv_rate = self.rng.normal(self.avg_conv_rate, self._avg_conv_rate / 4)
                print("new target: {}, conv_rate: {}".format(target_trend, conv_rate))
                spike_time = self.rng.exponential(self.avg_spike_period)
                print("next spike will trigger in {} seconds".format(spike_time))
                start = time.time()

            if self._reached_target(target_trend):
                print("target {} reached".format(target_trend))
                start_trend = trend
                target_trend = self.rng.uniform(self._min_regular_trend, self._max_regular_trend)
                conv_rate = self.rng.normal(self.avg_conv_rate, self._avg_conv_rate / 4)
                print("new target: {}, conv_rate: {}".format(target_trend, conv_rate))
                spike_time -= elapsed
                start = time.time()

            time.sleep(update_period)

    def _reached_target(self, target):
        return target - self.tolerance < trend < target + self.tolerance


if __name__ == '__main__':
    tread = TrendUpdaterThread(12345, 1)
    tread.start()
    while True:
        time.sleep(1)
        print("trend:", trend)
