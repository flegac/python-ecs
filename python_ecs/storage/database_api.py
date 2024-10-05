from abc import ABC, abstractmethod
from typing import Type

from python_ecs.component import Component
from python_ecs.component_set import ComponentSet
from python_ecs.signature import Signature
from python_ecs.storage.index import Index
from python_ecs.types import EntityId


class DatabaseAPI(ABC):

    @abstractmethod
    def entities(self) -> set[EntityId]:
        ...

    @abstractmethod
    def create_all(self, items: list[ComponentSet]):
        ...

    @abstractmethod
    def destroy_all(self, items: Component | Signature | list[Component | Signature]):
        ...

    @abstractmethod
    def get_table[T:Component | Signature](self, ttype: Type[T]) -> Index[T]:
        ...

    @abstractmethod
    def find_any[T: Component](self, what: Type[T], having: list[Type[Component]]) -> T:
        ...
