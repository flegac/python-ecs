import math
from typing import Self

import numpy as np
from pydantic import Field

from python_ecs.component import Component


class Vec3(Component):
    raw: np.ndarray = Field(default_factory=lambda: np.zeros((3,)))

    @classmethod
    def create(cls, x: float = 0, y: float = 0, z: float = 0):
        return cls(raw=np.array([x, y, z], dtype=float))

    @staticmethod
    def direction(a: 'Vec3', b: 'Vec3'):
        return Vec3(raw=b.raw - a.raw)

    @property
    def x(self):
        return self.raw[0]

    @property
    def y(self):
        return self.raw[1]

    @property
    def z(self):
        return self.raw[2]

    @x.setter
    def x(self, value: float):
        self.raw[0] = value

    @y.setter
    def y(self, value: float):
        self.raw[1] = value

    @z.setter
    def z(self, value: float):
        self.raw[2] = value

    def norm(self):
        # return np.linalg.vector_norm(self.raw)
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normal(self, size: float = 1.0):
        n = self.norm()
        if n == 0:
            return self
        return self * size / n

    @classmethod
    def random(cls, shape: Self = None):
        if shape is not None:
            return cls(raw=np.random.rand(3) * shape.raw)
        return cls(raw=np.random.rand(3))

    def __add__(self, other):
        if isinstance(other, Vec3):
            other = other.raw
        return self.__class__(raw=self.raw + other)

    def __iadd__(self, other):
        if isinstance(other, Vec3):
            other = other.raw
        self.raw += other
        return self

    def __sub__(self, other):
        if isinstance(other, Vec3):
            other = other.raw
        return self.__class__(raw=self.raw - other)

    def __isub__(self, other):
        if isinstance(other, Vec3):
            other = other.raw
        self.raw -= other
        return self

    def __mul__(self, other):
        if isinstance(other, Vec3):
            other = other.raw
        return self.__class__(raw=self.raw * other)

    def __imul__(self, other):
        if isinstance(other, Vec3):
            other = other.raw
        self.raw *= other
        return self

    def __truediv__(self, other):
        if isinstance(other, Vec3):
            other = other.raw
        return self.__class__(raw=self.raw / other)

    def __itruediv__(self, other):
        if isinstance(other, Vec3):
            other = other.raw
        self.raw /= other
        return self
