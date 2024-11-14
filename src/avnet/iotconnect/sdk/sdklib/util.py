import json
from dataclasses import fields, is_dataclass, field, dataclass
from datetime import datetime, timedelta


def filter_init(cls):
    """
    A decorator that modifies the __init__ method of a dataclass to accept a dictionary input.
    It filters out any keys in the input dictionary that are not defined as fields in the dataclass,
    allowing only specified fields to be set during initialization.

    Additionally, if a field is itself a dataclass and is provided as a nested dictionary,
    the decorator will recursively initialize the nested dataclass with the dictionary data.

    Parameters:
    cls : type
        The dataclass to decorate.

    Returns:
    type
        The decorated dataclass with a modified __init__ method.

    Example:
    --------
    @filter_init
    @dataclass
    class Example:
        field1: int
        field2: str

    data = {"field1": 10, "field2": "hello", "extra_field": "ignored"}
    obj = Example(data)  # Initializes Example(field1=10, field2="hello") and ignores "extra_field"
    """
    original_init = cls.__init__

    def __init__(self, input_dict):
        # Get all field names of the dataclass
        field_names = {f.name for f in fields(self)}
        # Filter the input dictionary to keep only the keys that are dataclass fields
        filtered_dict = {k: v for k, v in input_dict.items() if k in field_names}
        # Initialize nested dataclasses if necessary
        for fld in fields(self):
            # Check if the field is a dataclass and its value in input_dict is a dictionary
            if is_dataclass(fld.type) and isinstance(filtered_dict.get(fld.name), dict):
                # Recursively initialize the nested dataclass
                filtered_dict[fld.name] = fld.type(filtered_dict[fld.name])
        # Call the original __init__ with filtered arguments
        original_init(self, **filtered_dict)

    cls.__init__ = __init__
    return cls


@filter_init
@dataclass
class D:
    ec: int = field(default=0)  # Set a default value for Python 3.7 compatibility


@filter_init
@dataclass
class Main:
    d: D = field(default_factory=D)  # Use default_factory to handle nested dataclass initialization


def to_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


class Timing:
    def __init__(self):
        self.t = datetime.now()

    def diff_next(self) -> timedelta:
        now = datetime.now()
        ret = self.diff_with(now)
        self.t = now
        return ret

    def diff_now(self) -> timedelta:
        return datetime.now() - self.t

    def diff_with(self, t: datetime) -> timedelta:
        return t - self.t

    def lap(self, do_print=True) -> timedelta:
        ret = self.diff_next()
        if do_print:
            print("timing: ", ret)
        return ret
