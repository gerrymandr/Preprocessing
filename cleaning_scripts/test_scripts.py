import geopandas as gp
from shapely.geometry import Polygon, LinearRing
import matplotlib.pyplot as plt
from check_shapefile_connectivity import *
from county_split import *
from donut_removal import *
import string

test_connectivity = False
test_splitting = False
test_donuts = False

""" TEST THE CONNECTIVITY SCRIPT """
if test_connectivity:
    d1 = Polygon([(0, 0), (3, 0), (3, 1), (0, 1)])
    d2 = Polygon([(0, 2), (3, 2), (3, 3), (0, 3)])
    d3 = Polygon([(0, 0), (1, 0), (1, 3), (0, 3)])
    d4 = Polygon([(2, 0), (3, 0), (3, 3), (2, 3)])

    df = gp.GeoDataFrame({"ID":['a','b','c','d'], 'geometry':[d1,d2,d3,d4]})

    df.plot(edgecolor='black')
    plt.show()

    check_shapefile_connectivity(df)


""" TEST SPLITTING VTDS BY COUNTY SCRIPT """
if test_splitting:
    a1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    a2 = Polygon([(1, 0), (2, 0), (2, 1), (1, 1)])
    a3 = Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
    a4 = Polygon([(3, 0), (4, 0), (4, 1), (3, 1)])
    a5 = Polygon([(0, 1), (1, 1), (1, 2), (0, 2)])
    a6 = Polygon([(1, 1), (2, 1), (2, 2), (1, 2)])
    a7 = Polygon([(2, 1), (3, 1), (3, 2), (2, 2)])
    a8 = Polygon([(3, 1), (4, 1), (4, 2), (3, 2)])

    b1 = Polygon([(0, 0), (1, 0), (1, 1.5), (0, 1.5)])
    b2 = Polygon([(1, 0), (3, 0), (3, 1), (1, 1)])
    b3 = Polygon([(3, 0), (4, 0), (4, 2), (3, 2)])
    b4 = Polygon([(0, 1.5), (1, 1.5), (1, 2), (0, 2)])
    b5 = Polygon([(1, 1), (3, 1), (3, 2), (1, 2)])

    # try with all string columns
    vtds = gp.GeoDataFrame({"ID": list(string.ascii_lowercase)[:8],
                            "geometry": [a1,a2,a3,a4,a5,a6,a7,a8]})
    counties = gp.GeoDataFrame({"ID": list(string.ascii_lowercase)[:5],
                            "geometry": [b1,b2,b3,b4,b5]})
    split_vtds_by_county(vtd_dataframe=vtds, vtd_id_column="ID",
            county_dataframe=counties, county_id_column="ID")

    # try with a mix of string and int columns
    vtds = gp.GeoDataFrame({"ID": range(8),
                            "geometry": [a1,a2,a3,a4,a5,a6,a7,a8]})
    counties = gp.GeoDataFrame({"ID": list(string.ascii_lowercase)[:5],
                            "geometry": [b1,b2,b3,b4,b5]})
    split_vtds_by_county(vtd_dataframe=vtds, vtd_id_column="ID",
            county_dataframe=counties, county_id_column="ID", outputfilename="trytwo")

    # try with all type int columns
    vtds = gp.GeoDataFrame({"ID": range(8),
                            "geometry": [a1,a2,a3,a4,a5,a6,a7,a8]})
    counties = gp.GeoDataFrame({"ID": range(5),
                            "geometry": [b1,b2,b3,b4,b5]})
    split_vtds_by_county(vtd_dataframe=vtds, vtd_id_column="ID",
            county_dataframe=counties, county_id_column="ID", outputfilename="trythree")


""" TEST DONUT REMOVAL SCRIPT """
if test_donuts:
    i2 = [(1, 1), (2, 1), (2, 2), (1, 2)][::-1]
    d1 = Polygon([(0, 0), (3, 0), (3, 3), (0, 3)], [i2])
    d2 = Polygon([(1, 1), (1.5, 1), (1.5, 2), (1, 2)])
    d3 = Polygon([(1.5, 1), (2, 1), (2, 2), (1.5, 2)])
    d4 = Polygon([(3, 0), (5, 0), (5, 1), (4, 1), (4, 2), (5, 2), (5, 3), (3, 3)])
    d5 = Polygon([(4, 1), (5, 1), (5, 2), (4, 2)])

    df = gp.GeoDataFrame({"ID": list(string.ascii_lowercase)[:5],
                        'geometry':[d1,d2,d3,d4,d5]})

    df.plot(edgecolor='black')
    plt.show()

    simplify_geometries(df)
