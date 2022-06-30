import sys
from typing import Dict, List, Tuple

import pytest

from typepigeon import guard_generic_alias


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires Python 3.8 or greater")
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
