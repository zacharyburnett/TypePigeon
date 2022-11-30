from datetime import date, datetime, timedelta
from typing import Any

import pytest

from typepigeon.convert import convert_value


def test_convert_str():
    str_1 = convert_value("a", str)

    with pytest.raises(ValueError):
        convert_value("a", float)

    str_2 = convert_value(0.55, str)
    str_3 = convert_value(0.55, "str")
    str_4 = convert_value("a", Any)

    assert str_1 == "a"
    assert str_2 == "0.55"
    assert str_3 == "0.55"
    assert str_4 == "a"


def test_convert_number():
    float_1 = convert_value("0.55", float)
    float_2 = convert_value("0.55", "float")

    int_1 = convert_value(0.55, int)
    int_2 = convert_value("5", int)

    with pytest.raises(ValueError):
        convert_value("0.55", int)

    assert float_1 == 0.55
    assert float_2 == 0.55

    assert int_1 == 0
    assert int_2 == 5


def test_convert_collection():
    list_1 = convert_value("a", [str])
    list_2 = convert_value([1], str)
    list_3 = convert_value([1, 2, "3", "4"], [int])
    list_4 = convert_value([1, 2, "3", "4"], (int, str, float, str))
    list_5 = convert_value("[1, 2, 3]", (int, str, float))
    list_6 = convert_value("1, 2, 3", [int])
    list_7 = convert_value("test 1, test 2, test 3", [str])
    list_8 = convert_value(None, [])

    with pytest.raises(ValueError):
        convert_value([1, 2, "3", "4"], (int, str))

    with pytest.raises(ValueError):
        convert_value([1, 2, "3", "4"], (int, str, float, str, float))

    dict_1 = convert_value({"a": 2.5, "b": 4, 3: "18"}, {str: float})
    dict_2 = convert_value('{"a": 2.5, "b": 4, "3": 18}', {str: float})

    assert list_1 == ["a"]
    assert list_2 == "[1]"
    assert list_3 == [1, 2, 3, 4]
    assert list_4 == (1, "2", 3.0, "4")
    assert list_5 == (1, "2", 3.0)
    assert list_6 == [1, 2, 3]
    assert list_7 == ["test 1", "test 2", "test 3"]
    assert list_8 == []

    assert dict_1 == {"a": 2.5, "b": 4.0, "3": 18.0}
    assert dict_2 == {"a": 2.5, "b": 4.0, "3": 18.0}


def test_convert_datetime():
    datetime_1 = convert_value(datetime(2021, 3, 26, 0, 56), str)
    datetime_2 = convert_value("20210326T005600", datetime)
    datetime_3 = convert_value(datetime(2021, 3, 26), date)
    datetime_4 = convert_value("2020-11-07 09:38:16", datetime)

    date_1 = convert_value(date(2021, 3, 26), str)
    date_2 = convert_value("20210326T005600", date)
    date_3 = convert_value(date(2021, 3, 26), datetime)

    timedelta_1 = convert_value(timedelta(hours=13), str)
    timedelta_2 = convert_value(timedelta(hours=13), float)
    timedelta_3 = convert_value("00:00", timedelta)
    timedelta_4 = convert_value("20:15", timedelta)
    timedelta_5 = convert_value("13:20:15", timedelta)
    timedelta_6 = convert_value("01:13:20:15", timedelta)
    timedelta_7 = convert_value(15, timedelta)

    with pytest.raises(ValueError):
        convert_value("02:01:13:20:15", timedelta)

    assert datetime_1 == "2021-03-26 00:56:00"
    assert datetime_2 == datetime(2021, 3, 26, 0, 56)
    assert datetime_3 == date(2021, 3, 26)
    assert datetime_4 == datetime(2020, 11, 7, 9, 38, 16)

    assert isinstance(datetime_3, date) and not isinstance(datetime_3, datetime)

    assert date_1 == "2021-03-26"
    assert date_2 == date(2021, 3, 26)
    assert date_3 == datetime(2021, 3, 26)

    assert isinstance(date_3, datetime)

    assert timedelta_1 == "13:00:00.0"
    assert timedelta_2 == 13 * 3600
    assert timedelta_3 == timedelta(minutes=0, seconds=0)
    assert timedelta_4 == timedelta(minutes=20, seconds=15)
    assert timedelta_5 == timedelta(hours=13, minutes=20, seconds=15)
    assert timedelta_6 == timedelta(days=1, hours=13, minutes=20, seconds=15)
    assert timedelta_7 == timedelta(seconds=15)


def test_convert_bool():
    bool_1 = convert_value(0, bool)
    bool_2 = convert_value("test", bool)
    bool_3 = convert_value("False", bool)

    assert bool_1 is False
    assert bool_2 is True
    assert bool_3 is False


def test_convert_none():
    none_1 = convert_value(None, str)
    none_2 = convert_value(5, None)

    assert none_1 is None
    assert none_2 is None
