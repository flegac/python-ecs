from abc import abstractmethod
from dataclasses import field
from typing import Type, override

from easy_config.my_model import MyModel
from python_ecs.component import Component
from python_ecs.signature import Signature
from python_ecs.storage.database_api import DatabaseAPI


class BaseSystem(MyModel):
    periodicity_sec: float = 0  # expected (or minimum) time between two updates

    def at_interval(self, periodicity_sec: float):
        self.periodicity_sec = periodicity_sec
        return self

    @abstractmethod
    def update(self, db: DatabaseAPI, dt: float):
        ...


class System[T: Signature | Component](BaseSystem):
    _signature: Type[T] = None

    def update_single(self, db: DatabaseAPI, item: T, dt: float):
        pass

    def register(self, item: T):
        pass

    def unregister(self, item: T):
        pass

    @override
    def update(self, db: DatabaseAPI, dt: float):
        items = db.get_table(self._signature).list_all()
        for item in items:
            self.update_single(db, item, dt)


class SystemBag(System):
    name: str
    steps: list[System] = field(default_factory=list)

    def update(self, db: DatabaseAPI, dt: float):
        for _ in self.steps:
            _.update_all(db, dt)
