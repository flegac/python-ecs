from enum import Enum, auto
from typing import Type, Self, Iterable, NewType

from pydantic import Field, model_validator

from easy_lib.my_model import MyModel
from easy_lib.timing import time_func


class GenId:
    def __init__(self):
        self._next_id = 0

    def new_id(self):
        self._next_id += 1
        return self._next_id


ComponentId = NewType('ComponentId', int)
EntityId = NewType('EntityId', int)

CID_GEN = GenId()
EID_GEN = GenId()


class Component(MyModel):
    cid: ComponentId = Field(default_factory=CID_GEN.new_id)
    eid: EntityId = -1
    is_active: bool = True

    @property
    def type_id(self):
        return self.__class__

    def __str__(self):
        params = ', '.join(f"{k}: {v}" for k, v in self.__dict__.items() if k not in {'cid', 'eid'})
        return f'{self.type_id.__name__}({params})'

    def __repr__(self):
        return str(self)


class Components(MyModel):
    ctype: Type[Component]
    active: dict[EntityId, Component] = Field(default_factory=dict)
    inactive: dict[EntityId, Component] = Field(default_factory=dict)

    def remove(self, eid: EntityId):
        self.active.pop(eid, None)
        self.inactive.pop(eid, None)

    def remove_all(self, eids: Iterable[EntityId]):
        for _ in eids:
            self.remove(_)

    def add(self, eid: EntityId, component: Component):
        component.eid = eid
        if component.is_active:
            self.active[eid] = component
        else:
            self.inactive[eid] = component


class UpdateStatus(MyModel):
    dead_entities: set[EntityId] = Field(default_factory=set)
    new_entities: list[list[Component]] = Field(default_factory=list)

    @staticmethod
    def dead(eid: EntityId):
        return UpdateStatus(dead_entities={eid})

    @staticmethod
    def create(items: list[list[Component]]):
        return UpdateStatus(new_entities=items)

    @staticmethod
    def new(items: list[list[Component]]):
        return UpdateStatus(new_entities=items)

    @time_func
    def load(self, other: Self):
        if other is None:
            return
        self.dead_entities.update(other.dead_entities)
        self.new_entities.extend(other.new_entities)


class CFilter(str, Enum):
    requires_all = auto()
    requires_any = auto()
    match_all = auto()


class Signature(MyModel):

    @property
    def eid(self):
        name = self.field_names()[0]
        xxx = getattr(self, name)
        return EntityId(xxx.eid)

    @classmethod
    def signature(cls):
        return [_.annotation for _ in cls.model_fields.values()]

    @classmethod
    def field_names(cls):
        return list(cls.model_fields.keys())

    @classmethod
    def cast(cls, items: list[Component]):
        names = cls.field_names()
        res = cls.model_construct()
        for name, value in zip(names, items):
            setattr(res, name, value)
        return res

    @model_validator(mode='after')
    def post_init(self):
        for name, _ in self.model_fields.items():
            if not isinstance(_.annotation, type(Component)):
                raise ValueError(f'Signature: {name} type is [{_.annotation}] (must be a Component)')


class System[T: Signature](MyModel):
    signature: Type[T] | None = None
    cfilter: CFilter = CFilter.requires_all

    def cast(self, items: list[Component]) -> T:
        if self.signature is None:
            return items
        return self.signature.cast(items)

    @time_func
    def update_all(self, items: list[T]):
        status = UpdateStatus()
        for _ in items:
            status.load(self.update(_))
        return status

    def update(self, item: T) -> UpdateStatus | None:
        raise NotImplementedError

    def register(self, item: T):
        pass

    def unregister(self, item: T):
        pass


class ECS(MyModel):
    systems: list[System] = Field(default_factory=list)
    components: dict[Type[Component], Components] = Field(default_factory=dict)

    @time_func
    def new_entities(self, entities: list[list[Component]]):
        for components in entities:
            eid = EntityId(EID_GEN.new_id())
            for c in components:
                ctype = c.type_id
                if ctype not in self.components:
                    self.components[ctype] = Components(ctype=ctype)
                self.components[ctype].add(eid, c)

    @time_func
    def destroy(self, ids: Iterable[EntityId]):
        for c in self.components.values():
            c.remove_all(ids)

    def update(self):
        status = UpdateStatus()
        for sys in self.systems:
            # try:
            items = self.compute_components(sys)
            status.load(sys.update_all(items))
            # except Exception as e:
            #     logger.error(f'{sys.__class__.__name__}: {e}')
        self.destroy(status.dead_entities)
        self.new_entities(status.new_entities)

    @time_func
    def compute_components[T](self, sys: System[T]):
        match sys.cfilter:
            case CFilter.match_all:
                signature = list(self.components.keys())
                entities = self.entities
            case CFilter.requires_all:
                signature = sys.signature.signature()
                entities = self.common_entities(signature)
            case CFilter.requires_any:
                signature = sys.signature.signature()
                entities = self.union_entities(signature)
            case _:
                raise NotImplementedError
        return [
            sys.cast([self.components[_].active.get(eid) for _ in signature])
            for eid in entities
        ]

    @property
    @time_func
    def entities(self) -> set[EntityId]:
        return set().union(*[set(_.active.keys()) for _ in self.components.values()])

    @time_func
    def union_entities(self, signature: list[Type[Component]]):
        res = set()
        for _ in signature:
            res.update(self.components[_].active.keys())
        return res

    @time_func
    def common_entities(self, signature: list[Type[Component]]):
        if not signature:
            return set()
        first = signature[0]
        res = set(self.components[first].active.keys())
        for _ in signature[1:]:
            res.intersection_update(self.components[_].active.keys())
            if not res:
                return res
        return res


# default simulator
sim = ECS()
