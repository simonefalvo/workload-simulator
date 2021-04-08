import time
from threading import Thread

trend = 0


class TrendUpdaterThread(Thread):

    def __init__(self, convergence):
        Thread.__init__(self)
        self._convergence = convergence  # convergence rate

    @property
    def convergence(self):
        return self._convergence

    def run(self):
        start = time.time()
        while True:
            time.sleep(1)
            elapsed = time.time() - start
            self.update_trend(elapsed)

    def update_trend(self, elapsed):
        global trend
        # linear
        trend = self.convergence * elapsed


if __name__ == '__main__':
    t = TrendUpdaterThread(0.5)
    t.start()
    while True:
        time.sleep(1)
        print(trend)
