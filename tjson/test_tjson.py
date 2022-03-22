from unittest import TestCase
import warnings
from tjson.errors import TJSONWarning, TypeMismatchWarning, InvalidKeyWarning

from tjson.tjson import TJ


class TestNode(TestCase):
    def setUp(self):
        # Data contains something like a REST API's response
        self.data = {
            "success": True,
            "resultCount": 123,
            "nextPageToken": "abcdef",
            "cats": [
                {
                    "name": "Lord Whiskerton",
                    "age": 12,
                    "breed": "Maine Coon",
                    "photo": "https://placekitten.com/200/400",
                    "remainingLives": 4.3,
                    "likesTuna": False,
                    "favoriteSayings": ["meow", "purr"],
                    "extraProperties": {
                        "foo bar": "baz quux",
                        "hello": "world",
                    },
                },
                {
                    "name": "Lady Meowsalot",
                    "age": None,
                    "breed": "Burmese",
                    "photo": None,
                    "remainingLives": None,
                    "likesTuna": None,
                    "favoriteSayings": None,
                    "extraProperties": None,
                },
            ],
        }

        self.node = TJ(self.data, [], [])

        # TJSON warnings should cause test failures, unless actually expected
        warnings.simplefilter('error', TJSONWarning)

    def test_path(self):
        # The path is tracked right whether there's a warning or not
        assert self.node['cats'][0]['extraProperties']['foo bar'].path == ".cats[0].extraProperties['foo bar']"
        with self.assertRaises(InvalidKeyWarning):
            assert self.node['a'][1]['b'][2]['c'][3].path == '.a[1].b[2].c[3]'

    def test_bool(self):
        # Typical access patterns
        assert self.node['success'].value is True
        assert self.node['cats'][0]['likesTuna'].value is False
        assert self.node['cats'][0]['likesTuna'].bool.value is False

    def test_bool_null(self):
        # Meowsalot has a null value for this, which should come back as None when the type is unspecified
        assert self.node['cats'][1]['likesTuna'].value is None

        # When the type is specified, it should be False, with a warning
        with self.assertWarns(TypeMismatchWarning):
            assert self.node['cats'][1]['likesTuna'].bool.value is False

        # If the type is nullable, the warning goes away and the value is None
        assert self.node['cats'][1]['likesTuna'].bool_or_null.value is None

    def test_bool_bad_key(self):
        # Nonexistent keys return their default value and warn
        with self.assertWarns(InvalidKeyWarning):
            assert self.node['hello'].bool.value is False
        with self.assertWarns(InvalidKeyWarning):
            assert self.node['hello'].bool_or_null.value is None

    def test_string(self):
        # Typical access patterns
        assert self.node['nextPageToken'].value == "abcdef"
        assert self.node['cats'][0]['name'].value == "Lord Whiskerton"
        assert self.node['cats'][0]['name'].string.value == "Lord Whiskerton"

    def test_string_null(self):
        # Meowsalot has a null value for this, which should come back as None when the type is unspecified
        assert self.node['cats'][1]['photo'].value is None

        # When the type is specified, it should be the default value, with a warning
        with self.assertWarns(TypeMismatchWarning):
            assert self.node['cats'][1]['photo'].string.value == ""

        # If the type is nullable, the warning goes away and the value is None
        assert self.node['cats'][1]['photo'].string_or_null.value is None

    def test_string_bad_key(self):
        # Nonexistent keys return their default value and warn
        with self.assertWarns(InvalidKeyWarning):
            assert self.node['hello'].string.value == ""
        with self.assertWarns(InvalidKeyWarning):
            assert self.node['hello'].string_or_null.value is None

    def test_number(self):
        # Typical access patterns
        assert self.node['resultCount'].value == 123
        assert isinstance(self.node['resultCount'].value, int)
        assert isinstance(self.node['resultCount'].number.value, int)

        # Int and float are distinct, but under the cover they both get served by .number, because JSON doesn't differentiate
        assert isinstance(self.node['cats'][0]['remainingLives'].number.value, float)
        self.assertAlmostEqual(self.node['cats'][0]['remainingLives'].number.value, 4.3)

    def test_number_null(self):
        # Meowsalot has a null value for this, which should come back as None when the type is unspecified
        assert self.node['cats'][1]['age'].value is None

        # When the type is specified, it should be the default value, with a warning
        with self.assertWarns(TypeMismatchWarning):
            assert self.node['cats'][1]['age'].number.value == 0

        # If the type is nullable, the warning goes away and the value is None
        assert self.node['cats'][1]['age'].number_or_null.value is None

    def test_number_bad_key(self):
        # Nonexistent keys return their default value and warn
        with self.assertWarns(InvalidKeyWarning):
            # default value is int 0
            assert self.node['hello'].number.value == 0
        with self.assertWarns(InvalidKeyWarning):
            assert self.node['hello'].number_or_null.value is None

    def test_array(self):
        # Typical access patterns
        assert self.node['success'].value is True
        assert isinstance(self.node['cats'].value, list)
        assert len(self.node['cats'].value) == 2

    def test_array_iteration(self):
        assert [(it.path, it.value) for it in self.node['cats'][0]['favoriteSayings']] == [
            (".cats[0].favoriteSayings[0]", "meow"),
            (".cats[0].favoriteSayings[1]", "purr"),
        ]

    def test_array_null(self):
        # Meowsalot has a null value for this, which should come back as None when the type is unspecified
        assert self.node['cats'][1]['favoriteSayings'].value is None

        # When the type is specified, it should be the default value, with a warning
        with self.assertWarns(TypeMismatchWarning):
            assert self.node['cats'][1]['favoriteSayings'].array.value == []

        # If the type is nullable, the warning goes away and the value is None
        assert self.node['cats'][1]['favoriteSayings'].array_or_null.value is None

    def test_array_bad_key(self):
        # Nonexistent keys return their default value and warn
        with self.assertWarns(InvalidKeyWarning):
            assert self.node['hello'].array.value == []
        with self.assertWarns(InvalidKeyWarning):
            assert self.node['hello'].array_or_null.value is None

    def test_object(self):
        # Typical access patterns
        assert isinstance(self.node['cats'][0].value, dict)
        assert len(self.node['cats'][0].value) == 8  # 8 properties

    def test_object_iteration(self):
        assert [(it.path, it.value) for it in self.node['cats'][0]['extraProperties']] == [
            (".cats[0].extraProperties['foo bar']", "baz quux"),
            (".cats[0].extraProperties.hello", "world"),
        ]

    def test_object_null(self):
        # Meowsalot has a null value for this, which should come back as None when the type is unspecified
        assert self.node['cats'][1]['extraProperties'].value is None

        # When the type is specified, it should be the default value, with a warning
        with self.assertWarns(TypeMismatchWarning):
            assert self.node['cats'][1]['extraProperties'].object.value == {}

        # If the type is nullable, the warning goes away and the value is None
        assert self.node['cats'][1]['extraProperties'].object_or_null.value is None

    def test_object_bad_key(self):
        # Nonexistent keys return their default value and warn
        with self.assertWarns(InvalidKeyWarning):
            assert self.node['hello'].object.value == {}
        with self.assertWarns(InvalidKeyWarning):
            assert self.node['hello'].object_or_null.value is None
