import ast
from datetime import date, datetime, timedelta
from enum import Enum, EnumMeta
import json
from pathlib import Path
import sys
from typing import Any, Collection, Iterable, Mapping, Union

from dateutil.parser import parse as parse_date
from pyproj import CRS
from shapely import wkb, wkt
from shapely.geometry import shape as shapely_shape
from shapely.geometry.base import GEOMETRY_TYPES


def convert_value(value: Any, to_type: Union[type, Collection[type]]) -> Any:
    """
    convert a value to the specified type

    :param value: Python value
    :param to_type: type to convert to
    :return: converted value

    >>> convert_value(0.55, str)
    '0.55'
    >>> convert_value('0.55', float)
    0.55
    >>> convert_value('0.55', 'float')
    0.55
    >>> convert_value(0.55, int)
    0

    >>> convert_value([1], str)
    '[1]'
    >>> convert_value([1, 2, '3', '4'], [int])
    [1, 2, 3, 4]
    >>> convert_value([1, 2, '3', '4'], (int, str, float, str))
    (1, '2', 3.0, '4')

    >>> convert_value({'a': 2.5, 'b': 4, 3: '18'}, {str: float})
    {'a': 2.5, 'b': 4.0, '3': 18.0}

    >>> convert_value(datetime(2021, 3, 26), str)
    datetime(2021, 3, 26)
    >>> convert_value('20210326', datetime)
    '2021-03-26 00:00:00'
    >>> convert_value('01:13:20:00', timedelta)
    timedelta(days=1, hours=13, minutes=20, seconds=0)
    >>> convert_value(timedelta(hours=1), str)
    '01:00:00.0'
    >>> convert_value(timedelta(hours=1), int)
    3600

    >>> convert_value(CRS.from_epsg(4326), int)
    4326
    >>> convert_value(CRS.from_epsg(4326), str)
    GEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["Horizontal component of 3D system."],AREA["World."],BBOX[-90,-180,90,180]],ID["EPSG",4326]]
    >>> convert_value(4326, CRS)
    CRS.from_epsg(4326)
    """

    if isinstance(to_type, str):
        to_type = getattr(sys.modules['builtins'], to_type)

    if isinstance(value, Enum):
        value = value.name

    to_type = guard_generic_alias(to_type)

    if to_type is None:
        value = None
    elif to_type is Any:
        return value
    elif isinstance(to_type, Collection):
        collection_type = type(to_type)
        if collection_type is not EnumMeta:
            if not issubclass(collection_type, Mapping):
                if value is not None:
                    to_type = list(to_type)
                    if not isinstance(value, Iterable) or isinstance(value, str):
                        try:
                            evaluated_value = ast.literal_eval(value)
                            assert isinstance(evaluated_value, Collection)
                            value = evaluated_value
                        except:
                            if isinstance(value, str) and ',' in value:
                                value = value.split(',')
                            else:
                                value = [value]
                    if len(to_type) == 1:
                        to_type = [to_type[0] for _ in value]
                    elif len(to_type) == len(value):
                        to_type = to_type[: len(value)]
                    else:
                        raise ValueError(
                            f'unable to convert list of values of length {len(value)} '
                            f'to list of types of length {len(to_type)}: '
                            f'{value} -/> {to_type}'
                        )
                    value = collection_type(
                        convert_value(value[index], current_type)
                        for index, current_type in enumerate(to_type)
                    )
                else:
                    value = collection_type()
            elif isinstance(value, str):
                value = json.loads(value)
            elif isinstance(value, CRS):
                value = value.to_json_dict()
            elif isinstance(value, Mapping):
                converted_items = []
                key_to_type = list(to_type)[0]
                value_to_type = to_type[key_to_type]
                for key, value in value.items():
                    key = convert_value(key, key_to_type)
                    value = convert_value(value, value_to_type)
                    converted_items.append((key, value))
                value = collection_type(converted_items)
        elif value is not None:
            try:
                value = to_type[value]
            except (KeyError, ValueError):
                try:
                    value = to_type(value)
                except (KeyError, ValueError):
                    raise ValueError(
                        f'unrecognized entry "{value}"; must be one of {list(to_type)}'
                    )
    elif not isinstance(value, to_type) and value is not None:
        if isinstance(value, timedelta):
            if issubclass(to_type, str):
                hours, remainder = divmod(value, timedelta(hours=1))
                minutes, remainder = divmod(remainder, timedelta(minutes=1))
                seconds = remainder / timedelta(seconds=1)
                value = f'{hours:02}:{minutes:02}:{seconds:04.3}'
            else:
                value /= timedelta(seconds=1)
        elif isinstance(value, CRS):
            if issubclass(to_type, str):
                value = value.to_wkt()
            elif issubclass(to_type, dict):
                value = value.to_json_dict()
            elif issubclass(to_type, int):
                value = value.to_epsg()
        if issubclass(to_type, bool):
            value = ast.literal_eval(f'{value}')
        elif issubclass(to_type, (datetime, date)):
            value = parse_date(value)
            if issubclass(to_type, date) and not issubclass(to_type, datetime):
                value = value.date()
        elif issubclass(to_type, timedelta):
            try:
                try:
                    time = datetime.strptime(value, '%H:%M:%S')
                    value = timedelta(
                        hours=time.hour, minutes=time.minute, seconds=time.second
                    )
                except:
                    parts = [float(part) for part in value.split(':')]
                    if len(parts) > 3:
                        days = parts.pop(0)
                    else:
                        days = 0
                    value = timedelta(
                        days=days, hours=parts[0], minutes=parts[1], seconds=parts[2]
                    )
            except:
                value = timedelta(seconds=float(value))
        elif to_type.__name__ in GEOMETRY_TYPES:
            try:
                value = wkb.loads(value, hex=True)
            except:
                try:
                    value = wkt.loads(value)
                except:
                    try:
                        value = wkb.loads(value)
                    except TypeError:
                        if isinstance(value, str):
                            value = ast.literal_eval(value)
                        try:
                            value = shapely_shape(value)
                        except:
                            value = to_type(value)
        elif issubclass(to_type, bool):
            try:
                value = ast.literal_eval(f'{value}')
            except:
                value = bool(value)

        if not isinstance(value, to_type):
            if isinstance(value, timedelta):
                if issubclass(to_type, str):
                    hours, remainder = divmod(value, timedelta(hours=1))
                    minutes, remainder = divmod(remainder, timedelta(minutes=1))
                    seconds = remainder / timedelta(seconds=1)
                    value = f'{hours:02}:{minutes:02}:{seconds:04.3}'
                else:
                    value /= timedelta(seconds=1)
            elif isinstance(value, CRS):
                if issubclass(to_type, str):
                    value = value.to_wkt()
                elif issubclass(to_type, dict):
                    value = value.to_json_dict()
                elif issubclass(to_type, int):
                    value = value.to_epsg()
            elif type(value).__name__ in GEOMETRY_TYPES and to_type.__name__ in GEOMETRY_TYPES:
                raise NotImplementedError('casting between geometric types not implemented')
            elif isinstance(value, (str, bytes)):
                try:
                    value = to_type.from_string(value)
                except:
                    value = to_type(value)
            else:
                value = to_type(value)

    return value


def convert_to_json(value: Any) -> Union[str, float, int, dict, list, bool]:
    """
    convert the given value to a JSON-compatible format

    :param value: value to convert
    :return: JSON value

    >>> convert_to_json(5)
    5
    >>> convert_to_json('5')
    '5'

    >>> convert_to_json(datetime(2021, 3, 26))
    '2021-03-26 00:00:00'

    >>> convert_to_json([5, '6', {3: datetime(2021, 3, 27)}])
    [5, '6', {3: '2021-03-27 00:00:00'}]
    >>> convert_to_json({'test': [5, '6', {3: datetime(2021, 3, 27)}]})
    {'test': [5, '6', {3: '2021-03-27 00:00:00'}]}
    """

    if isinstance(value, Path):
        value = value.as_posix()
    elif isinstance(value, Enum):
        value = value.name
    if type(value) not in (float, int, bool, str):
        if isinstance(value, Collection) and not isinstance(value, str):
            if isinstance(value, Mapping):
                value = {
                    convert_to_json(key): convert_to_json(entry)
                    for key, entry in value.items()
                }
            else:
                value = [convert_to_json(entry) for entry in value]
        else:
            try:
                value = convert_value(value, float)
            except:
                try:
                    value = convert_value(value, int)
                except:
                    try:
                        value = convert_value(value, bool)
                    except:
                        value = convert_value(value, str)
    return value


def guard_generic_alias(generic_alias) -> type:
    """
    convert an instance of a subscripted ``typing._GenericAlias`` to a subscripted type

    :param generic_alias: generic alias
    :return: simple type

    >>> from typing import List
    >>> guard_generic_alias(List[str])
    [str]

    >>> from typing import Dict
    >>> guard_generic_alias(Dict[str, float])
    {str: float}

    >>> from typing import Dict, Tuple
    >>> guard_generic_alias({str: (Dict[int, str], str)})
    {str: ({int: str}, str)}

    """

    if hasattr(generic_alias, '__origin__'):
        type_class = generic_alias.__origin__
        if hasattr(generic_alias, '__args__'):
            members = generic_alias.__args__
            if issubclass(type_class, Mapping):
                members = [members]
        else:
            members = ()
    elif isinstance(generic_alias, Collection) and not isinstance(
        generic_alias, (EnumMeta, str)
    ):
        type_class = generic_alias.__class__
        if issubclass(type_class, Mapping):
            members = generic_alias.items()
        else:
            members = generic_alias
    else:
        return generic_alias

    members = [guard_generic_alias(member) for member in members]
    if type_class != generic_alias.__class__ or members != generic_alias:
        return type_class(members)
    else:
        return generic_alias
