import functools
from typing import Self, Type, ClassVar

from easy_kit.timing import time_func
from pydantic import Field, model_validator

from easy_config.my_model import MyModel
from python_ecs.id_generator import IdGenerator
from python_ecs.types import ComponentId, EntityId

CID_GEN = IdGenerator()


class Component(MyModel):
    cid: ComponentId = Field(default_factory=CID_GEN.new_id)
    eid: EntityId = -1
    is_active: bool = True

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

    @property
    def entity(self):
        from python_ecs.ecs import sim
        return sim.entity(self.eid)

    def __str__(self):
        params = ', '.join(f"{k}: {v}" for k, v in self.__dict__.items() if k not in {'cid', 'eid'})
        return f'{self.type_id.__name__}({params})'

    def __repr__(self):
        return str(self)


class Signature(MyModel):

    @property
    def eid(self):
        name = self.field_names()[0]
        item = getattr(self, name)
        return EntityId(item.eid)

    @classmethod
    @functools.lru_cache()
    def signature(cls) -> list[Type[Component]]:
        return [_.annotation for _ in cls.model_fields.values()]

    @classmethod
    @functools.lru_cache()
    def field_names(cls):
        return list(cls.model_fields.keys())

    @classmethod
    @time_func
    def field_mapping(cls):
        return dict(zip(cls.signature(), cls.field_names()))

    @classmethod
    def match(cls, items: list[Component]):
        mapping = cls.field_mapping()
        for item in items:
            name = mapping.pop(item.type_id)
        return len(mapping) == 0

    @classmethod
    @time_func
    def cast(cls, items: list[Component]):
        mapping = cls.field_mapping()
        if len(items) < len(mapping):
            return None

        res = cls.model_construct()
        for item in items:
            name = mapping.pop(item.type_id, None)
            if name is not None:
                setattr(res, name, item)
        if len(mapping) > 0:
            return None
        return res

    @model_validator(mode='after')
    def post_init(self):
        for name, _ in self.model_fields.items():
            if not isinstance(_.annotation, type(Component)):
                raise ValueError(f'Signature: {name} type is [{_.annotation}] (must be a Component)')
