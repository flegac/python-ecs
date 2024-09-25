from dataclasses import field
from typing import Type

from easy_kit.timing import timing
from pydantic import model_validator

from easy_config.my_model import MyModel
from python_ecs.component import Component, Signature
from python_ecs.entity_filter import FilterStrategy
from python_ecs.storage.database import Database


class System[T: Signature | Component](MyModel):
    _signature: Type[T] = None
    _filter_strategy: FilterStrategy = FilterStrategy.requires_all
    periodicity_sec: float = 0  # expected (or minimum) time between two updates

    def at_interval(self, periodicity_sec: float):
        self.periodicity_sec = periodicity_sec
        return self

    def update_single(self, db: Database, item: T, dt: float):
        pass

    def update_before(self, db: Database, dt: float):
        pass

    def update_after(self, db: Database, dt: float):
        pass

    def register(self, item: T):
        pass

    def unregister(self, item: T):
        pass

    def update(self, db: Database, dt: float):
        # with timing(f'ECS.{self.__class__.__name__}'):
        with timing(f'ECS.{self.__class__.__name__}.update_before'):
            self.update_before(db, dt)
        with timing(f'ECS.{self.__class__.__name__}.update_all'):
            self.update_all(db, dt)
        with timing(f'ECS.{self.__class__.__name__}.update_after'):
            self.update_after(db, dt)

    def update_all(self, db: Database, dt: float):
        if self._filter_strategy is FilterStrategy.match_none:
            items = []
        else:
            items = list(db.get_index(self).items.values())
            # items = list(self.items.values())

        for item in items:
            self.update_single(db, item, dt)

    def cast(self, items: list[Component]):
        if self._signature is None:
            return items
        return self._signature.cast(items)

    @model_validator(mode='after')
    def post_init(self):
        if self._filter_strategy is FilterStrategy.match_none:
            return self
        if self._filter_strategy is FilterStrategy.match_all:
            return self

        if not isinstance(self._signature, type):
            raise ValueError(f'{self.__class__}: Undefined signature: {self._signature}')
        return self


class SystemBag(System):
    _filter_strategy = FilterStrategy.match_none
    subsystems: list[System] = field(default_factory=list)

    def update_all(self, db: Database, dt: float):
        for _ in self.subsystems:
            _.update_all(db, dt)
