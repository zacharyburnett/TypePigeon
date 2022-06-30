import json
import sys

import pytest

from tests import REFERENCE_DIRECTORY
from typepigeon import convert_value


@pytest.mark.spatial
@pytest.mark.skipif(
    sys.version_info < (3, 8), reason="mismatch in WKT strings in PROJ versions"
)
def test_convert_crs():
    from pyproj import CRS

    reference_directory = REFERENCE_DIRECTORY / "test_convert_crs"

    crs_1 = convert_value(CRS.from_epsg(4326), str)
    crs_2 = convert_value(CRS.from_epsg(4326), int)
    crs_3 = convert_value(CRS.from_epsg(4326), dict)
    crs_4 = convert_value(CRS.from_epsg(4326), {})
    crs_5 = convert_value(4326, CRS)

    wkt_filename = reference_directory / "epsg4326.txt"
    json_filename = reference_directory / "epsg4326.json"

    with open(wkt_filename) as wkt_file:
        reference_crs_wkt = wkt_file.read()
    with open(json_filename) as json_file:
        reference_crs_json = json.load(json_file)

    assert crs_1 == reference_crs_wkt
    assert crs_2 == 4326
    assert crs_3 == reference_crs_json
    assert crs_4 == reference_crs_json
    assert crs_5 == CRS.from_epsg(4326)


@pytest.mark.spatial
def test_convert_geometry():
    from shapely.geometry import LineString, MultiPoint, Point, Polygon

    geometry_1 = convert_value("[0, 1]", Point)
    geometry_2 = convert_value((0, 1), Point)
    geometry_3 = convert_value([(0, 1), (1, 1), (1, 0), (0, 0)], MultiPoint)
    geometry_4 = convert_value([(0, 1), (1, 1), (1, 0), (0, 0)], LineString)
    geometry_5 = convert_value([(0, 1), (1, 1), (1, 0), (0, 0)], Polygon)

    with pytest.raises(TypeError):
        convert_value(Point(0, 1), MultiPoint)

    assert geometry_1 == Point((0, 1))
    assert geometry_2 == Point((0, 1))
    assert geometry_3 == MultiPoint([(0, 1), (1, 1), (1, 0), (0, 0)])
    assert geometry_4 == LineString([(0, 1), (1, 1), (1, 0), (0, 0)])
    assert geometry_5 == Polygon([(0, 1), (1, 1), (1, 0), (0, 0)])
