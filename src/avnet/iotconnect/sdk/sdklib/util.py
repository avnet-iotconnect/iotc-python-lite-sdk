# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/


import json
from dataclasses import fields, is_dataclass
from datetime import datetime, timedelta


def dict_filter_empty(input_dict: dict):
    return {k: v for k, v in input_dict.items() if v is not None}


def dataclass_factory_filter_empty(data):
    return {key: value for key, value in data if value is not None}


def to_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o)))
    )


def add_from_dict(cls):
    def from_dict_function(input_dict):
        field_names = {fld.name for fld in fields(cls)}
        field_types = {fld.name: fld.type for fld in fields(cls)}
        processed_fields = {}

        for key, value in input_dict.items():
            if key in field_names:
                field_type = field_types[key]
                if hasattr(field_type, '__origin__') and field_type.__origin__ == list:
                    # Handle list of dataclasses
                    inner_type = field_type.__args__[0]
                    if hasattr(inner_type, 'from_dict'):
                        processed_fields[key] = [inner_type.from_dict(item) for item in value]
                    else:
                        processed_fields[key] = value
                else:
                    processed_fields[key] = value
        return cls(**processed_fields)

    cls.from_dict = from_dict_function
    return cls


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

    def reset(self, do_print=True) -> timedelta:
        ret = self.diff_next()
        if do_print:
            print("timing: ", ret)
        return ret
