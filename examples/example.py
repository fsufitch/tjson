import json
from tjson.container import TJ
from tjson.json_typing import Number

json_input = b"""
{
    "foo": "bar",
    "hello": "world",
    "things": ["first", "second", "third"],
    "otherThings": {
        "wow": 123,
        "float!": 456
    },
    "very": {"deeply": {"nested": {"stuff": [
        "ready",
        "set",
        true,
        false,
        null
    ]}}}
}

"""

j = TJ(json.loads(json_input))

print(j.value)
bar = j["foo"]
print(bar)
print(bar.value)

