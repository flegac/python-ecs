from datetime import datetime


class Periodic:
    def __init__(self, period_sec: float):
        self.period_sec = period_sec
        self.last_activation: datetime = datetime.now()  # datetime.fromtimestamp(0)

    def check_activation(self):
        now = datetime.now()
        delta = now - self.last_activation
        activation = delta.total_seconds() >= self.period_sec
        if activation:
            self.last_activation = now
        return activation
