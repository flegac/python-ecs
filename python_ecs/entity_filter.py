from enum import Enum
from typing import Type

from python_ecs.component import Signature
from python_ecs.selection_strategy import EntitySelectionStrategy, SelectAll, SelectUnion, SelectIntersection, \
    SelectNone
from python_ecs.storage.database import Database


class FilterStrategy(Enum):
    requires_all = SelectIntersection()
    requires_any = SelectUnion()
    match_all = SelectAll()
    match_none = SelectNone()

    def __init__(self, strategy: EntitySelectionStrategy):
        self.strategy = strategy

    def select(self, db: Database, sign: Type[Signature] | None):
        return self.value.select(db, sign)
