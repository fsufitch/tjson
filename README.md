# `tjson` &mdash; An access utility for typed "JSON-shaped" Python objects

Have you had to deal with deeply nested JSON documents in Python, only to be greeted by `KeyError`? What about only to run across weird type issues, and mysterious bugs? Have you wished that you could easily get type hinting on values that you pull out of your JSON documents? `tjson` is here to help.

[![Python package](https://github.com/fsufitch/tjson/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/fsufitch/tjson/actions/workflows/python-package.yml) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


## Installing

`tjson` has no dependencies outside the standard Python library. Simply install it with Pip or your favorite dependency manager.

    pip install tj_json

> `tjson` is taken on PyPI by a dead project, and I haven't bothered to take over the name.

## Usage

`tjson`'s API  is designed to be intuitive and simple.

```py
>>> from tjson.tjson import TJ
```

`TJ` is a generic wrapper for JSON values. Simply give it your "JSON-shaped" Python values to get started.

> **Note: `tjson` is an access utility, not a parser/deserializer.** To parse your JSON, you must still use a parser such as the standard library's `json`.

```py
>>> mydata = TJ({'who': 'the quick brown fox', 'what': 'jumped', 'where': ['over', 'the lazy dog'], 'timestamp': 12345.123})
```

### Traversal and access

To traverse `TJ`, simply use Python's item accessor `[]`. All usees of it return a new instance of `TJ` pointing to the new value. To retrieve the value wrapped by `TJ`, just check its `.value`.

```py
>>> mydata['where'][1]
<tjson.tjson.TJ object at 0x7f02148e2f20>
>>> mydata['where'][1].value
'the lazy dog'
```

`TJ` objects also store the path that they followed to reach them, and that can be queried using `.path`.

```py
>>> mydata['where'][1].path
'.where[1]'
```

### When things go wrong: Warnings

When using regular Python `dict`/`list` strucures, trying to access a bad key or index results in exceptions. This makes you need either over-broad or over-nitpicky exception handling, and makes code smell. `tjson` instead relegates problems accessing our JSON documents as warnings, taking advantage of Python's smart [`warnings` feature set](https://docs.python.org/3/library/warnings.html).

When access to the underlying object fails, a `TJ` instance is created anyway, just wrapping the value `None`. Additionally, an appropriate warning is fired off using `warnings.warn`, and the warnings are collected in the `.warnings` property of the `TJ`.

```py
>>> print(*mydata['who']['entities'][123]['name'].warnings, sep="\n")

<stdin>:1: InvalidKeyWarning: Tried to access str key 'entities' of non-object at path `.who`

Tried to access str key 'entities' of non-object at path `.who`
Cannot access int index 123 of non-array at path .who.entities
Tried to access str key 'name' of non-object at path `.who.entities[123]`
```

> Only the first warning in a chain of warnings is actually sent to `warnings.warn`. This is to avoid flooding if an error happens early in a complex access chain.

If you want the bad accesses to raise warnings instead, you can use the `warnings` API to enable the specific class:

```py
>>> import warnings
>>> from tjson.errors import InvalidKeyWarning
>>> warnings.simplefilter('error', InvalidKeyWarning)
>>> mydata['who']['entities'][123]['name']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/fsufitch/code/tjson/tjson/tjson.py", line 30, in __getitem__
    return TJ(None, next_path, _amend_warns(self.warnings, InvalidKeyWarning(f"Tried to access str key {repr(key)} of non-object at path `{self.path}`"), 2))
  File "/home/fsufitch/code/tjson/tjson/tjson.py", line 123, in _amend_warns
    warn(warning, stacklevel=stacklevel + 1)
tjson.errors.InvalidKeyWarning: Tried to access str key 'entities' of non-object at path `.who`
```

Refer to the standard library's `warnings` documentation for more usages.

### Type assertion

Another way to use the `TJ` objects is to have them check the type of value you are accessing. Consider this case of Bob refusing to play the game properly:

```py
>>> high_scores = {'Alice': 123, 'Bob': None, 'Charlie': 456}
>>> alice_score = high_scores['Alice']
>>> bob_score = high_scores['Bob']
>>> charlie_score = high_scores['Charlie']
>>> print(max(alice_score, bob_score, charlie_score))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: '>' not supported between instances of 'NoneType' and 'int'
```

`TJ` can come to the rescue, using the `.number` assertion to create a copy of itself that checks that it _actually_ contains a number! Like with access problems, any issue results in a warning, and the `TJ` containing the default value of the appropriate type (in this case, `0`).

```py
>>> high_scores = TJ({'Alice': 123, 'Bob': None, 'Charlie': 456})
>>> alice_score = high_scores['Alice'].number.value
>>> bob_score = high_scores['Bob'].number.value
<stdin>:1: TypeMismatchWarning: Cannot cast to int|float at path `.Bob`
>>> charlie_score = high_scores['Charlie'].number.value
>>> print(max(alice_score, bob_score, charlie_score))
456
```

No more error! But what if you wanted `None` to actually be a valid value? That's cool, you can use `.number_or_null` instead, and `None` will be considered a "technically valid" value for the number.

The type assertions supported this way correspond to the different types in JSON, plus their "nullable" versions. They map to the following Python type hints:

* `bool` &rarr; `bool`
* `bool_or_null` &rarr; `Optional[bool]`
* `string` &rarr; `str`
* `string_or_null` &rarr; `Optional[str]`
* `number` &rarr; `int | float`  
* `number_or_null` &rarr; `Optional[int | float]`
* `array` &rarr; `List[...]`
* `array_or_null` &rarr; `Optional[List[...]]`
* `object` &rarr; `Dict[str, ...]`
* `object_or_null` &rarr; `Optional[Dict[str, ...]]` 

> Note: JSON does not distinguish between integer and floating point numbers, so `tjson` does not either. If your code cares, you need to handle it separately.

> Note: The only valid object keys in JSON are strings. Integers are not valid object keys, and need to be wrapped in strings to be used as such.

### Type hints for your IDE

`tjson` is built using type hints on all the right places. Your IDE should be able to pick these up in order to provide you a rich type checking experience.

For example, using PyLance in Visual Studio Code, I can see that my string operation is potentially unsafe since I might be adding `None` to a string:

![](./type_hint_example.png)

### More...?

`tjson` has good test coverage. Check its tests (`test_*.py`) to see all the features.

## License: MIT

Like `tjson`? Do what you like with it, just give credit.

Don't like it? Think it's pointless or trivial? That's probably fair, but it's here anyway.

## Enjoy, and happy coding!
