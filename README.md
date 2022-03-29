# TypePigeon

[![tests](https://github.com/zacharyburnett/TypePigeon/workflows/tests/badge.svg)](https://github.com/zacharyburnett/TypePigeon/actions?query=workflow%3Atests)
[![codecov](https://codecov.io/gh/zacharyburnett/TypePigeon/branch/main/graph/badge.svg?token=4DwZePHp18)](https://codecov.io/gh/zacharyburnett/TypePigeon)
[![build](https://github.com/zacharyburnett/TypePigeon/workflows/build/badge.svg)](https://github.com/zacharyburnett/TypePigeon/actions?query=workflow%3Abuild)
[![version](https://img.shields.io/pypi/v/TypePigeon)](https://pypi.org/project/TypePigeon)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/typepigeon/badges/version.svg)](https://anaconda.org/conda-forge/typepigeon)
[![license](https://img.shields.io/github/license/zacharyburnett/TypePigeon)](https://creativecommons.org/share-your-work/public-domain/cc0)
[![style](https://sourceforge.net/p/oitnb/code/ci/default/tree/_doc/_static/oitnb.svg?format=raw)](https://sourceforge.net/p/oitnb/code)

TypePigeon is a Python type converter focused on converting values between
various Python data types.

```shell
pip install typepigeon
```

## Features

- convert values directly from one Python type to another with `convert_value()`
- convert values to JSON format with `convert_to_json()`
- convert generic aliases (`List[str]`) to simple collection types (`[str]`)
  with `guard_generic_alias()`

## Usage

With TypePigeon, you can convert simple values from one type to another:

### `convert_value()`

```python
import typepigeon

typepigeon.convert_value(0.55, str)
'0.55'

typepigeon.convert_value(1, float)
1.0

typepigeon.convert_value([1], str)
'[1]'
```

Additionally, you can also cast values into a collection:

```python
import typepigeon

typepigeon.convert_value([1, 2.0, '3'], [int])
[1, 2, 3]

typepigeon.convert_value('[1, 2, 3]', (int, str, float))
[1, '2', 3.0]

typepigeon.convert_value({'a': 2.5, 'b': 4, 3: '18'}, {str: float})
{'a': 2.5, 'b': 4.0, '3': 18.0}
```

Some commonly-used classes such as `datetime` and `CRS` are also supported:

```python
from datetime import datetime, timedelta

from pyproj import CRS
import typepigeon

typepigeon.convert_value(datetime(2021, 3, 26), str)
'2021-03-26 00:00:00'

typepigeon.convert_value('20210326', datetime)
datetime(2021, 3, 26)

typepigeon.convert_value('01:13:20:00', timedelta)
timedelta(days=1, hours=13, minutes=20, seconds=0)

typepigeon.convert_value(timedelta(hours=1), str)
'01:00:00.0'

typepigeon.convert_value(timedelta(hours=1), int)
3600

typepigeon.convert_value(CRS.from_epsg(4326), int)
4326

typepigeon.convert_value(CRS.from_epsg(4326), str)
'GEOGCRS["WGS 84",ENSEMBLE["World Geodetic System 1984 ensemble",MEMBER["World Geodetic System 1984 (Transit)"],MEMBER["World Geodetic System 1984 (G730)"],MEMBER["World Geodetic System 1984 (G873)"],MEMBER["World Geodetic System 1984 (G1150)"],MEMBER["World Geodetic System 1984 (G1674)"],MEMBER["World Geodetic System 1984 (G1762)"],ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]],ENSEMBLEACCURACY[2.0]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],USAGE[SCOPE["Horizontal component of 3D system."],AREA["World."],BBOX[-90,-180,90,180]],ID["EPSG",4326]]'

typepigeon.convert_value(4326, CRS)
CRS.from_epsg(4326)
```

### `convert_to_json()`

```python
from datetime import datetime

import typepigeon

typepigeon.convert_to_json(5)
5

typepigeon.convert_to_json('5')
'5'

typepigeon.convert_to_json(datetime(2021, 3, 26))
'2021-03-26 00:00:00'

typepigeon.convert_to_json([5, '6', {3: datetime(2021, 3, 27)}])
[5, '6', {3: '2021-03-27 00:00:00'}]

typepigeon.convert_to_json({'test': [5, '6', {3: datetime(2021, 3, 27)}]})
{'test': [5, '6', {3: '2021-03-27 00:00:00'}]}
```

### `guard_generic_alias()`

```python
from typing import Dict, List, Tuple

import typepigeon

typepigeon.guard_generic_alias(List[str])
[str]

typepigeon.guard_generic_alias(Dict[str, float])
{str: float}

typepigeon.guard_generic_alias({str: (Dict[int, str], str)})
{str: ({int: str}, str)}
```