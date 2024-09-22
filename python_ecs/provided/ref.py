from typing import Any

from pydantic import Field

from python_ecs.component import Component


class Ref[T](Component):
    ref: T


class Refs(Component):
    refs: dict[str, Any] = Field(default_factory=dict)
