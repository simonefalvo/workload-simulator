import time
from threading import Thread

trend = 0
stop = False


class TrendUpdaterThread(Thread):

    def __init__(self, convergence, tick):
        Thread.__init__(self)
        self._convergence = convergence  # convergence rate
        self._tick = tick  # trend update period

    @property
    def convergence(self):
        return self._convergence

    @property
    def tick(self):
        return self._tick

    def run(self):
        start = time.time()
        update_period = self.tick
        while not stop:
            time.sleep(update_period)
            elapsed = time.time() - start
            self.update_trend(elapsed)

    def update_trend(self, elapsed):
        global trend
        # linear
        trend = self.convergence * elapsed


if __name__ == '__main__':
    t = TrendUpdaterThread(0.5, 1)
    t.start()
    while True:
        time.sleep(1)
        print(trend)
