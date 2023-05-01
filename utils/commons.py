"""
@file commons.py
@author Antony Chiossi
"""


import string

from django.forms import ValidationError


def is_int(value: int, min: int = None, max: int = None, default: int = None):
    if not isinstance(value, int):
        if default is not None:
            return default
        raise ValidationError(
            ("%(value)s is not an integer"),
            params={"value": value},
        )
    if min is not None and value < min:
        raise ValidationError(
            ("%(value)s min is %(min)d"),
            params={"value": value, "mi": min},
        )
    if max is not None and value > max:
        raise ValidationError(
            ("%(value)s max is %(max)d"),
            params={"value": value, "max": max},
        )


def is_str(value: str, minLen: int = None, maxLen: int = None, default: int = None):
    if not isinstance(value, str) or len(value) == 0:
        if default is not None:
            return default
        raise ValidationError(
            ("%(value)s is not a string"),
            params={"value": value},
        )
    if minLen is not None and len(value) < minLen:
        raise ValidationError(
            ("%(value)s min len is %(minLen)d"),
            params={"value": value, "minLen": minLen},
        )
    if maxLen is not None and len(value) > maxLen:
        raise ValidationError(
            ("%(value)s min len is %(maxLen)d"),
            params={"value": value, "maxLen": maxLen},
        )


def snowflake_to_base62(snowflake_id: int) -> str:
    """
    This function converts a snowflake ID (represented in hexadecimal) to a base62 string.

    :param snowflake_id: The snowflake_id parameter is a string representing a unique identifier
    generated by Twitter's Snowflake algorithm. It is typically a 64-bit integer represented in
    hexadecimal format
    :return: a base62 representation of a given snowflake ID.
    """
    print(snowflake_id, int(str(snowflake_id), 16))
    base62_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
    base10 = int(str(snowflake_id), 16)
    base62 = []
    while base10 > 0:
        # Divide the base10 number by 62 using bitwise right shift operator (>>),
        # and get the remainder using bitwise AND operator (&) with a mask of 0x3F.
        base10, remainder = base10 >> 6, base10 & 0x3F
        base62.append(base62_alphabet[remainder])
    print(len(base62))
    return "".join(reversed(base62))
