from typing import Type

from easy_kit.timing import timing
from pydantic import model_validator

from easy_config.my_model import MyModel
from python_ecs.component import Component, Signature
from python_ecs.entity_filter import FilterStrategy
from python_ecs.storage.database import Database
from python_ecs.update_status import Demography


class System[T: Signature | Component](MyModel):
    _signature: Type[T] = None
    _filter_strategy: FilterStrategy = FilterStrategy.requires_all
    periodicity_sec: float = 0  # expected (or minimum) time between two updates

    def at_interval(self, periodicity_sec: float):
        self.periodicity_sec = periodicity_sec
        return self

    def update_single(self, item: T, dt: float) -> Demography:
        pass

    def update_before(self, db: Database, dt: float) -> Demography:
        pass

    def update_after(self, db: Database, dt: float) -> Demography:
        pass

    def register(self, item: T) -> Demography:
        pass

    def unregister(self, item: T) -> Demography:
        pass

    def update(self, db: Database, dt: float) -> Demography:
        # with timing(f'ECS.update.{self.__class__.__name__}'):
        status = Demography()
        with timing(f'ECS.update.{self.__class__.__name__}.update_before'):
            status.load(self.update_before(db, dt))
        with timing(f'ECS.update.{self.__class__.__name__}.update_all'):
            status.load(self.update_all(db, dt))
        with timing(f'ECS.update.{self.__class__.__name__}.update_after'):
            status.load(self.update_after(db, dt))
        return status

    def update_all(self, db: Database, dt: float):
        status = Demography()
        if self._filter_strategy is FilterStrategy.match_none:
            items = []
        else:
            items = list(db.get_index(self).items.values())
            # items = list(self.items.values())

        for item in items:
            status.load(self.update_single(item, dt))
        return status

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
