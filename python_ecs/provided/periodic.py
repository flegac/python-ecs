import random
from datetime import datetime


class Periodic:
    def __init__(self, period_sec: float, desync_sec: float = .1):
        self.period_sec = period_sec
        self.desync = desync_sec
        self.last_activation: datetime = datetime.now()  # datetime.fromtimestamp(0)

    def check_activation(self):
        now = datetime.now()

        variation = random.random() * 2 - 1

        delta = now - self.last_activation
        activation = delta.total_seconds() >= self.period_sec + variation * self.desync
        if activation:
            self.last_activation = now
        return activation
