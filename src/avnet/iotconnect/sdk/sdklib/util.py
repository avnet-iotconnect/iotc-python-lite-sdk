# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/


from dataclasses import fields, is_dataclass
from datetime import datetime, timedelta
from typing import get_type_hints, Type, Union, TypeVar


def dict_filter_empty(input_dict: dict):
    return {k: v for k, v in input_dict.items() if v is not None}


def dataclass_factory_filter_empty(data):
    return {key: value for key, value in data if value is not None}


T = TypeVar("T")


def deserialize_dataclass(cls: Type[T], data: Union[dict, list]) -> T:
    """
    Recursively deserialize data into a dataclass or a list of dataclasses.
    """
    if isinstance(data, list):
        # Handle lists of dataclasses
        inner_type = cls.__args__[0] if hasattr(cls, '__args__') else None
        if inner_type and is_dataclass(inner_type):
            return [deserialize_dataclass(inner_type, item) for item in data]
        return data

    if isinstance(data, dict) and is_dataclass(cls):
        field_types = get_type_hints(cls)
        return cls(
            **{
                key: deserialize_dataclass(field_types[key], value)
                if key in field_types and _is_optional_or_dataclass(field_types[key], value)
                else (
                    deserialize_dataclass(field_types[key], value)
                    if key in field_types
                       and hasattr(field_types[key], '__origin__')
                       and field_types[key].__origin__ == list
                    else value
                )
                for key, value in data.items()
                if key in field_types  # Ignore unexpected fields
            }
        )
    return data


def _is_optional_or_dataclass(field_type, value):
    """
    Check if a field type is either an Optional or a dataclass.
    """
    if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
        # Check for Optional[Type]
        inner_types = field_type.__args__
        if len(inner_types) == 2 and type(None) in inner_types:
            inner_type = [t for t in inner_types if t is not type(None)][0]
            return is_dataclass(inner_type)
    return is_dataclass(field_type)


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
