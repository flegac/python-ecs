from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Periodic:
    period_sec: float
    last_activation: datetime = field(default_factory=datetime.now)

    def get_phase(self):
        now = datetime.now()
        delta = now - self.last_activation

        return (delta.total_seconds() % self.period_sec) / self.period_sec

    def check_activation(self):
        now = datetime.now()

        delta = now - self.last_activation
        activation = delta.total_seconds() >= self.period_sec
        if activation:
            self.last_activation = now
        return activation
