from abc import ABC, abstractmethod
from typing import Type

from easy_lib.my_model import MyModel
from python_ecs.component import Component, Signature
from python_ecs.storage.database import Database
from python_ecs.types import EntityId


class EntitySelectionStrategy(MyModel, ABC):

    @abstractmethod
    def select(self, db: Database, sign: list[Type[Component]]) -> tuple[list[Type[Component]], set[EntityId]]:
        ...


class SelectAll(EntitySelectionStrategy):
    def select(self, db: Database, sign: Type[Signature] | None):
        signature = list(db.components.keys())
        entities = db.entities
        return signature, entities


class SelectNone(EntitySelectionStrategy):
    def select(self, db: Database, sign: list[Type[Component]]):
        return [], set()


class SelectUnion(EntitySelectionStrategy):

    def select(self, db: Database, sign: Type[Signature] | None):
        signature = sign.signature()

        entities = db.union_entities(signature)
        return signature, entities


class SelectIntersection(EntitySelectionStrategy):
    def select(self, db: Database, sign: Type[Signature] | None):
        signature = sign.signature()
        entities = db.common_entities(signature)
        return signature, entities
