from __future__ import annotations
from warnings import warn
from typing import DefaultDict, Dict, List, Mapping, Optional, Type, TypeVar, Union, Any as PyAny

from tjson.errors import TypeMismatchWarning

Unknown = object

Null = type(None)
Boolean = bool


class String(str):
    ...


class NumberInt(int):
    ...


class NumberFloat(float):
    ...


class Array(List[Unknown]):
    ...


class Object(Dict[String, Unknown]):
    ...


Number = Union[NumberInt, NumberFloat]
Value = Union[Null, Boolean, String, Number, Array, Object]
UnknownValue = Union[Unknown, Value]

JTYPE_MAP: Mapping[Type, Type[UnknownValue]] = DefaultDict()
JTYPE_MAP.update({
    bool: Boolean,
    str: String,
    int: NumberInt,
    float: NumberFloat,
    list: Array,
    dict: Object,
})
JTYPE_MAP.default_factory = lambda: Unknown

_JTYPE_NAMES = {
    Null: "null",
    Boolean: "Boolean",
    String: "String",
    Number: "Number",
    NumberInt: "Number(int)",
    NumberFloat: "Number(float)",
    Array: "Array",
    Object: "Object",
}


def jtype_name(t: Type) -> str:
    name = _JTYPE_NAMES.get(t)
    if not name:
        name = f"<js-incompatible {repr(t)}>"
    return name


_T = TypeVar("_T")


def jtype_zero_value(t: Type[_T]) -> _T:
    print(t)
    if t is Unknown:
        return None  # type: ignore
    if (t is type(None) or issubclass(t, (Boolean, String, Number, Array, Object))) and callable(t):  # type: ignore
        return t()
    raise TypeError(f"Not a JSON type: {repr(t)}")


def jtype_cast(value: UnknownValue, to_type: Type[_T]) -> _T:
    print(value, "->", to_type)
    if isinstance(value, to_type):
        return value
    warn(TypeMismatchWarning(f"Cannot cast value of type {type(value)} to type {jtype_name(to_type)}"))
    return jtype_zero_value(to_type)
