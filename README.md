# TypePigeon

[![tests](https://github.com/zacharyburnett/TypePigeon/workflows/tests/badge.svg)](https://github.com/zacharyburnett/TypePigeon/actions?query=workflow%3Atests)
[![codecov](https://codecov.io/gh/zacharyburnett/TypePigeon/branch/main/graph/badge.svg?token=4DwZePHp18)](https://codecov.io/gh/zacharyburnett/TypePigeon)
[![build](https://github.com/zacharyburnett/TypePigeon/workflows/build/badge.svg)](https://github.com/zacharyburnett/TypePigeon/actions?query=workflow%3Abuild)
[![version](https://img.shields.io/pypi/v/TypePigeon)](https://pypi.org/project/TypePigeon)
[![license](https://img.shields.io/github/license/zacharyburnett/TypePigeon)](https://creativecommons.org/share-your-work/public-domain/cc0)
[![style](https://sourceforge.net/p/oitnb/code/ci/default/tree/_doc/_static/oitnb.svg?format=raw)](https://sourceforge.net/p/oitnb/code)

TypePigeon is a Python type converter focused on converting values between various Python data types.

```shell
pip install typepigeon
```

## Features

- convert values directly from one Python type to another with `convert_value()`
- convert values to JSON format with `convert_to_json()`
- convert generic aliases (`List[str]`) to simple collection types (`[str]`) with `guard_generic_alias()`

## Usage

With TypePigeon, you can convert simple values from one type to another:

```python
import typepigeon

typepigeon.convert_value(0.55, str)
# '0.55'

typepigeon.convert_value(1, float)
# 1.0

typepigeon.convert_value([1], str)
# '[1]'
```

Additionally, you can also cast values into a collection:

```python
import typepigeon

typepigeon.convert_value([1, 2.0, '3'], [int])
# [1, 2, 3]

typepigeon.convert_value('[1, 2, 3]', (int, str, float))
# [1, '2', 3.0]
```
