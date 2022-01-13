from datetime import datetime, timedelta
from enum import Enum
import json
import os
import sys
from typing import Any, Dict, List, Tuple

from pyproj import CRS
import pytest
from shapely.geometry import LineString, MultiPoint, Point, Polygon

from tests import REFERENCE_DIRECTORY
from typepigeon.convert import convert_to_json, convert_value, guard_generic_alias


class ValueTest:
    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other: 'ValueTest') -> bool:
        return self.value == other.value


class FloatTest:
    def __init__(self, value: int):
        self.value = value

    def __str__(self) -> str:
        return f'{self.value}'

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)


class IntegerTest:
    def __init__(self, value: int):
        self.value = value

    def __int__(self) -> int:
        return int(self.value)


class EnumerationTest(Enum):
    test_1 = 'test_1'


def test_convert_value():
    reference_directory = REFERENCE_DIRECTORY / 'test_convert_value'

    str_1 = convert_value('a', str)

    with pytest.raises(ValueError):
        convert_value('a', float)

    str_2 = convert_value(0.55, str)
    str_3 = convert_value(0.55, 'str')
    str_4 = convert_value('a', Any)

    float_1 = convert_value('0.55', float)
    float_2 = convert_value('0.55', 'float')

    int_1 = convert_value(0.55, int)
    int_2 = convert_value('5', int)

    with pytest.raises(ValueError):
        convert_value('0.55', int)

    list_1 = convert_value('a', [str])
    list_2 = convert_value([1], str)
    list_3 = convert_value([1, 2, '3', '4'], [int])
    list_4 = convert_value([1, 2, '3', '4'], (int, str, float, str))
    list_5 = convert_value('[1, 2, 3]', (int, str, float))

    with pytest.raises(ValueError):
        convert_value([1, 2, '3', '4'], (int, str))

    with pytest.raises(ValueError):
        convert_value([1, 2, '3', '4'], (int, str, float, str, float))

    dict_1 = convert_value({'a': 2.5, 'b': 4, 3: '18'}, {str: float})

    datetime_1 = convert_value(datetime(2021, 3, 26), str)
    datetime_2 = convert_value('20210326', datetime)

    timedelta_1 = convert_value(timedelta(hours=1), str)
    timedelta_2 = convert_value(timedelta(hours=1), float)
    timedelta_3 = convert_value('00:00:00:00', timedelta)
    timedelta_4 = convert_value('01:13:20:00', timedelta)

    class_1 = convert_value(5, ValueTest)
    class_2 = convert_value('test_1', EnumerationTest)

    none_1 = convert_value(None, str)
    none_2 = convert_value(5, None)

    crs_1 = convert_value(CRS.from_epsg(4326), str)
    crs_2 = convert_value(CRS.from_epsg(4326), int)
    crs_3 = convert_value(CRS.from_epsg(4326), dict)
    crs_4 = convert_value(4326, CRS)

    geometry_1 = convert_value('[0, 1]', Point)
    geometry_2 = convert_value((0, 1), Point)
    geometry_3 = convert_value([(0, 1), (1, 1), (1, 0), (0, 0)], MultiPoint)
    geometry_4 = convert_value([(0, 1), (1, 1), (1, 0), (0, 0)], LineString)
    geometry_5 = convert_value([(0, 1), (1, 1), (1, 0), (0, 0)], Polygon)

    with pytest.raises(NotImplementedError):
        convert_value(Point(0, 1), MultiPoint)

    with pytest.raises((KeyError, ValueError)):
        convert_value(5, EnumerationTest)

    assert str_1 == 'a'
    assert str_2 == '0.55'
    assert str_3 == '0.55'
    assert str_4 == 'a'

    assert float_1 == 0.55
    assert float_2 == 0.55

    assert int_1 == 0
    assert int_2 == 5

    assert list_1 == ['a']
    assert list_2 == '[1]'
    assert list_3 == [1, 2, 3, 4]
    assert list_4 == (1, '2', 3.0, '4')
    assert list_5 == (1, '2', 3.0)

    assert dict_1 == {'a': 2.5, 'b': 4.0, '3': 18.0}

    assert datetime_1 == '2021-03-26 00:00:00'
    assert datetime_2 == datetime(2021, 3, 26)

    assert timedelta_1 == '01:00:00.0'
    assert timedelta_2 == 3600
    assert timedelta_3 == timedelta(seconds=0)
    assert timedelta_4 == timedelta(days=1, hours=13, minutes=20, seconds=0)

    assert class_1 == ValueTest(5)
    assert class_2 == EnumerationTest.test_1

    assert none_1 is None
    assert none_2 is None

    if os.name == 'nt':
        wkt_filename = reference_directory / 'epsg4326_windows.txt'
        json_filename = reference_directory / 'epsg4326_windows.json'
    elif sys.version_info < (3, 8):
        wkt_filename = reference_directory / 'epsg4326_python36.txt'
        json_filename = reference_directory / 'epsg4326_python36.json'
    else:
        wkt_filename = reference_directory / 'epsg4326.txt'
        json_filename = reference_directory / 'epsg4326.json'

    with open(wkt_filename) as wkt_file:
        reference_crs_wkt = wkt_file.read()
    with open(json_filename) as json_file:
        reference_crs_json = json.load(json_file)

    assert crs_1 == reference_crs_wkt
    assert crs_3 == reference_crs_json
    assert crs_2 == 4326
    assert crs_4 == CRS.from_epsg(4326)

    assert geometry_1 == Point((0, 1))
    assert geometry_2 == Point((0, 1))
    assert geometry_3 == MultiPoint([(0, 1), (1, 1), (1, 0), (0, 0)])
    assert geometry_4 == LineString([(0, 1), (1, 1), (1, 0), (0, 0)])
    assert geometry_5 == Polygon([(0, 1), (1, 1), (1, 0), (0, 0)])


def test_convert_values_to_json():
    result_1 = convert_to_json(5)
    result_2 = convert_to_json('5')

    result_3 = convert_to_json(FloatTest(5))
    result_4 = convert_to_json(IntegerTest(5.0))
    result_5 = convert_to_json(FloatTest(5.5))

    result_6 = convert_to_json('test')
    result_7 = convert_to_json(datetime(2021, 3, 26))

    result_8 = convert_to_json(
        convert_to_json([FloatTest(5), '6', {3: datetime(2021, 3, 27)}])
    )
    result_9 = convert_to_json(
        convert_to_json({'test': [FloatTest(5), '6', {3: datetime(2021, 3, 27)}]})
    )

    assert result_1 == 5
    assert result_2 == '5'

    assert result_3 == 5.0
    assert result_4 == 5
    assert result_5 == 5.5

    assert result_6 == 'test'
    assert result_7 == '2021-03-26 00:00:00'

    assert result_8 == [5, '6', {3: '2021-03-27 00:00:00'}]
    assert result_9 == {'test': [5, '6', {3: '2021-03-27 00:00:00'}]}


@pytest.mark.skipif(sys.version_info < (3, 8), reason='requires Python 3.8 or greater')
def test_generic_alias():
    subscripted_type_1 = guard_generic_alias(List[str])
    subscripted_type_2 = guard_generic_alias(Tuple[str, float])
    subscripted_type_3 = guard_generic_alias(Dict[str, int])

    mixed_type_1 = guard_generic_alias([str])
    mixed_type_2 = guard_generic_alias([Tuple[float, List[int]]])
    mixed_type_3 = guard_generic_alias({str: Tuple[str, int]})
    mixed_type_4 = guard_generic_alias({str: (Dict[int, str], str)})

    assert subscripted_type_1 == [str]
    assert subscripted_type_2 == (str, float)
    assert subscripted_type_3 == {str: int}

    assert mixed_type_1 == [str]
    assert mixed_type_2 == [(float, [int])]
    assert mixed_type_3 == {str: (str, int)}
    assert mixed_type_4 == {str: ({int: str}, str)}
