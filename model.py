import numpy as np


class User:

    def __init__(self, sensor_id, name, email, rng_seed, avg_event_period, var_event_period):
        # Generate user data
        self._sensor_id = sensor_id
        self._name = name
        self._email = email
        self._rng = np.random.default_rng(rng_seed)
        self._avg_event_period = int(self.rng.normal(avg_event_period, var_event_period))

    @property
    def rng(self):
        return self._rng

    @property
    def name(self):
        return self._name

    @property
    def sensor_id(self):
        return self._sensor_id

    @property
    def avg_event_period(self):
        return self._avg_event_period

    @property
    def email(self):
        return self._email


if __name__ == '__main__':
    for i in range(10):
        user = User(1, "test", "test@example.com", i, 60, 10)
        print(user.avg_event_period)
    n = 30
    sum = 0
    for i in range(n):
        val = np.random.exponential(user.avg_event_period)
        print(val)
        sum = sum + val

    print("avg:", sum/n)