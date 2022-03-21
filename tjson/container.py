from __future__ import annotations
from functools import singledispatchmethod
from warnings import warn
from typing import Generic, NamedTuple, Tuple, Type, TypeVar, Union
from tjson import json_typing as jt
from tjson.errors import InvalidKeyWarning

_T = TypeVar('_T', bound=jt.UnknownValue)
_R = TypeVar('_R', bound=jt.UnknownValue)


class TJ(Generic[_T]):
    def __init__(self, value: _T):
        self.value = value

    def cast(self, to_type: Type[_R]) -> "TJ[_R]":
        if to_type is jt.Unknown:
            return TJ(self.value)
        return TJ(jt.jtype_cast(self.value, to_type))

    def __getitem__(self, key: Union[int, str, Tuple[Union[int, str], Type[_R]]]):
        if isinstance(key, (int, str)):
            return self[key, jt.Unknown]
        key, expect_type = key
        if isinstance(key, int):
            return self.__array_get(key, expect_type)
        if isinstance(key, str):
            return self.__object_get(key, expect_type)
        raise TypeError(f"Invalid key type; expected int or str, got: {type(key)}")

    def __array_get(self, key: int, expected_type: Type[_R]) -> "TJ[_R]":
        tj_arr = self.cast(jt.Array)
        if key < 0 or key >= len(tj_arr.value):
            warn(InvalidKeyWarning(f"Array key out of bounds: {key}"))
            return TJ(jt.jtype_zero_value(expected_type))
        return TJ(jt.jtype_cast(tj_arr.value[key], expected_type))
        
    def __object_get(self, key: str, expected_type: Type[_R]) -> "TJ[_R]":
        tj_obj = self.cast(jt.Object)
        if key not in tj_obj.value:
            warn(InvalidKeyWarning(f"Object key missing: {key}"))
            print(tj_obj.value)
            print(key)
            return TJ(jt.jtype_zero_value(expected_type))
        return TJ(jt.jtype_cast(tj_obj.value[key], expected_type))
