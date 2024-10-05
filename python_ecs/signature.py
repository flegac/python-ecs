import functools
from typing import Type

from pydantic import model_validator

from easy_config.my_model import MyModel
from easy_kit.timing import time_func
from python_ecs.component import Component
from python_ecs.types import EntityId


class Signature(MyModel):
    @property
    def eid(self):
        name = self.field_names()[0]
        item = getattr(self, name)
        return EntityId(item.eid)

    def to_components(self) -> list[Component]:
        return list(filter(None, [
            getattr(self, name)
            for name in self.field_names()
        ]))

    @classmethod
    @time_func
    @functools.lru_cache()
    def signature(cls) -> list[Type[Component]]:
        return [cls.model_fields[_].annotation for _ in cls.field_names()]

    @classmethod
    @functools.lru_cache()
    def field_names(cls):
        return list(sorted(cls.model_fields.keys()))

    @classmethod
    @time_func
    # @functools.lru_cache()
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
        return self