from typing import Self, Type, Any

from pydantic import Field

from easy_config.my_model import MyModel
from easy_kit.timing import time_func
from python_ecs.storage.id_generator import IdGenerator
from python_ecs.types import ComponentId, EntityId

CID_GEN = IdGenerator()


class Component(MyModel):
    cid: ComponentId = Field(default_factory=CID_GEN.new_id)
    eid: EntityId = -1

    db: Any = None

    @classmethod
    def signature(cls) -> list[Type[Self]]:
        return [cls]

    @classmethod
    @time_func
    def cast(cls, items: list[Self]):
        for item in items:
            if isinstance(item, cls):
                return item

    @property
    def type_id(self):
        return self.__class__

    def get[T:Component](self, ctype: Type[T]) -> T | None:
        return self.db.get_table(ctype).read(self.eid)
