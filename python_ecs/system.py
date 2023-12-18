from typing import Type

from pydantic import Field

from easy_lib.my_model import MyModel
from easy_lib.timing import time_func, timing
from python_ecs.component import Component, Signature
from python_ecs.entity_filter import EntityFilter
from python_ecs.storage.database import Database
from python_ecs.types import EntityId
from python_ecs.update_status import UpdateStatus


class System[T: Signature | Component](MyModel):
    _signature: Type[T] | None = None
    _filter_strategy = EntityFilter.requires_all
    items: dict[EntityId, T] = Field(default_factory=dict)

    def update_single(self, item: T) -> UpdateStatus | None:
        pass

    def update_before(self, db: Database) -> UpdateStatus | None:
        pass

    def update_after(self, db: Database) -> UpdateStatus | None:
        pass

    def update_demography(self, status: UpdateStatus):
        if self._signature is None:
            return

        for _ in status.death:
            item = self.items.pop(_, None)
            if item:
                self.unregister(item)
        for _ in status.birth:
            if isinstance(_, Component):
                _ = [_]
            item = self.cast(_)
            if item is not None:
                self.auto_register(item)

    def register(self, item: T):
        pass

    def unregister(self, item: T):
        pass

    def update(self, db: Database) -> UpdateStatus:
        with timing(f'{self.__class__.__name__}.update'):
            status = UpdateStatus()
            status.load(self.update_before(db))
            status.load(self.update_all(db))
            status.load(self.update_after(db))
            return status

    def update_all(self, db: Database):
        status = UpdateStatus()
        items = list(self.items.values())
        if self._filter_strategy is EntityFilter.match_none:
            items = []

        for item in items:
            status.load(self.update_single(item))
        return status

    def cast(self, items: list[Component]):
        if self._signature is None:
            return items
        return self._signature.cast(items)

    @time_func
    def auto_register(self, item: T):
        if item.eid in self.items:
            return
        self.items[item.eid] = item
        self.register(item)
