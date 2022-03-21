from __future__ import annotations
from abc import ABC, abstractmethod, abstractstaticmethod
from functools import singledispatch
from typing import Any, Dict, List, Mapping, Optional, Type, TypeVar, Generic, Union
from warnings import warn

from tjson.errors import TypeMismatchWarning


_JSONValue = Union[None, bool, str, int, float, list, dict]
_T = TypeVar('_T', bound=_JSONValue)
_R = TypeVar('_R', bound=_JSONValue)

class _Wrapper(ABC, Generic[_T]):
    zero: _T
    def __init__(self, value: _T) -> None:
        self._value = value
    
    def __cast_failed(self, to_type_wrapper: Type[_Wrapper[_R]]) -> _R:
        warn(TypeMismatchWarning(f"{type(self)} is not a {to_type_wrapper}"))
        return to_type_wrapper.zero

    def null(self):
        return self.__cast_failed(Null)

    def bool(self):
        return self.__cast_failed(Bool)

    def number(self):
        return self.__cast_failed(Number)

    def string(self):
        return self.__cast_failed(String)

    def array(self):
        return self.__cast_failed(Array)

    def object(self):
        return self.__cast_failed(Object)

class Null(_Wrapper[None]):
    zero = None
    def null(self):
        return self._value

class Bool(_Wrapper[bool]):
    zero = False
    def bool(self):
        return self._value

class Number(_Wrapper[Union[int, float]]):
    zero = 0
    def number(self):
        return self._value

class String(_Wrapper[str]):
    zero = ''
    def string(self):
        return self._value

class Array(_Wrapper[list]):
    zero = []
    def array(self):
        return self._value

class Object(_Wrapper[dict]):
    zero = {}
    def object(self):
        return self._value


def wrap(val: _JSONValue):
    if val is None:
        return Null(val)
    elif isinstance(val, bool):
        return Bool(val)
    elif isinstance(val, (int, float)):
        return Number(val)
    elif isinstance(val, str):
        return String(val)
    elif isinstance(val, list):
        return Array(val)
    elif isinstance(val, dict):
        return Object(val)
    raise TypeError()



