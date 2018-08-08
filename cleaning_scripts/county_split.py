"""
   Author: Mary Barker

   This code takes two shapefiles (labeled as vtds and counties respectively)
   and checks that the vtds do NOT overlap with multiple counties.

   If they do, it splits the vtd geometry that overlaps with mutliple,
   and labels the resulting split sections with the original id of the unit
   it came from, and the county it lies in.

   main function:
       :split_vtds_by_county: reads in the files, creates lookup, and splits
      
   auxiliary functions: 
       :fasterLookupTable: creates a spatial correspondence lookup between two shapefiles
"""
import numpy as np
import pandas as pd
import geopandas as gp


def fasterLookupTable(largerShapes, smallerShapes, largeIDCol, smallIDCol, by_area=False):
    """Create lookup between largerShapes geoseries and smallerSahapes geoseries
    inputs:
        :largerShapes: geodataframe with larger units
        :smallerShapes: geodataframe with smaller units
        :largeIDCol: unique identifier for largerShapes units
        :smallIDCol: unique identifier for smallerShapes units
    returns:
        pandas dataframe with 3 columns:
        - smallerShapes units id
        - largerShapes units id
        - the area of the geometry that is shared between them.
    """

    lookupTable=[]
    g1 = gp.GeoSeries(smallerShapes['geometry'])
    g2 = gp.GeoSeries(largerShapes['geometry'])

    for i in smallerShapes.index:
        namei = smallerShapes.loc[i, smallIDCol]
        geomi = g1[i]

        minArea = 0.0
        assignedj = None
        for j in largerShapes.index:
            namej = largerShapes.loc[j, largeIDCol]
            geomj = g2[j]

            if geomj.contains(geomi):
                minArea = geomi.area
                assignedj = namej
            else:
                area = geomj.intersection(geomi).area
                if not by_area and (area > minArea):
                    minArea = area
                    assignedj = namej
                elif by_area and (area > 0):
                    lookupTable.append((namei, namej, area))
                    assignedj = None
        if assignedj:
            lookupTable.append((namei, assignedj, minArea))
    return pd.DataFrame(lookupTable, index=None, columns=["small", "large", "area"])


def split_vtds_by_county(vtd_dataframe=None, vtd_shapefile=None, vtd_id_column=None,
                        county_dataframe=None, county_shapefile=None, county_id_column=None,
                        outputfilename="split_by_county"):

    # read the files in
    if (vtd_dataframe is None) and vtd_shapefile is not None:
        vtds = gp.read_file(vtd_shapefile)
    elif vtd_dataframe is not None:
        vtds = vtd_dataframe
    else:
        print("split_vtds_by_county takes 2 shapefile or GeoDataFrame arguments.\naborting...")
        return

    if (county_dataframe is None) and county_shapefile is not None:
        counties = gp.read_file(county_shapefile)
    elif county_dataframe is not None:
        counties = vtd_dataframe
    else:
        print("split_vtds_by_county takes 2 shapefile or GeoDataFrame arguments.\naborting...")
        return

    print("read the files in")

    # create lookup table
    lookup = fasterLookupTable(counties, vtds, county_id_column, vtd_id_column, by_area=True)
    lookup.to_csv("lookupTableVTDSToCounties.csv")
    print("created lookup and printed it out")

    new_df_geoids   = []
    new_df_counties = []
    new_df_geoms    = []

    vtds = vtds.set_index(vtd_id_column)
    counties = counties.set_index(county_id_column)

    for vtd in vtds.index.tolist():

        if vtd in lookup['small']:
            myslice = lookup.loc[(lookup['small'] == vtd) & (lookup['area'] > 1.0e-8), :]
            g1 = vtds.geometry[vtd]

            for county in myslice['large'].unique():
                g2 = counties.geometry[county]
                g = g1.intersection(g2)

                new_df_geoids.append(vtd)
                new_df_counties.append(county)
                new_df_geoms.append(g)
        else:
            new_df_geoids.append(vtd)
            new_df_counties.append(None)
            new_df_geoms.append(vtds.geometry[vtd])

    gp.GeoDataFrame({
        "ID": range(len(new_df_geoids)),
        "GEOID": new_df_geoids,
        "COUNTY": new_df_counties,
        "geometry": gp.GeoSeries(new_df_geoms)}).to_file(outputfilename.split('.shp')[0])
