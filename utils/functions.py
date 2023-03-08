from enum import Enum


def asdict_enum_to_value(data):
    return {
        field: value.value if isinstance(value, Enum) else value for field, value in data
    }
