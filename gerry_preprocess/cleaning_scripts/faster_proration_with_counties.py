"""
    Author: Mary Barker

    This code does proration of values from one shapefile to another with a performance
    boost. 

    It requires that both of the shapefiles involved in the proration, 
    the one with values to prorate, AND the one to prorate values into, 

    MUST have a field in common that identifies groups of geometries that are 
    in the same area. 
    
    e.g. Congressional districts that are assigned to both counties and to vtds. 

    The code first groups all units by congressional district,
    and then creates a lookup table of geographic overlap correspondence 
    between the shapes before prorating. 


    Use case example:

    two shapefiles VTDS.shp and COUNTIES.shp: 
       * VTDS.shp has congressional districts in a column called "CD"
       * COUNTIES.shp has them in a column called "CongDist"

    want 'VOTES' column data from COUNTIES.shp in VTDS.shp

    then call 
    prorate_grouped_by_column_value("VTDS.shp", "COUNTIES.shp", "CD", "CongDist", ["VOTES"], "Prorated.shp")

    to generate a shapefile called "Prorated.shp" with the "VOTES" column data

"""
import geopandas as gp
import pandas as pd
import numpy as np
import os


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

        minArea = geomi.area * 0.5
        assignedj = None
        for j in largerShapes.index:
            namej = largerShapes.loc[j, largeIDCol]
            geomj = g2[j]
            if geomj.intersection(geomi).area > minArea:
                assignedj = namej
        if assignedj:
            lookupTable.append((namei, assignedj, minArea))

    return pd.DataFrame(lookupTable, index=None, columns=["small", "large", "area"])


def prorate_grouped_by_column_value(chain_units_path, data_units_path, chain_groupby_name, data_groupby_name, prorate_cols, output_file_name):
    """
        when prorating two very large shapefiles, it speeds things up a lot if they have 
        something in common. This does proration based on that shared value. 

        e.g. prorating population data from blocks to vtds. Both sets of geographic units
        had a 'county' column, so instead of searching all vtds to all blocks, the code
        went by county and for each vtd in a county looked at the blocks in the county.

        This gives a massive performance boost, but requires that both shapefiles have 
        an extra column that behaves nicely (i.e. is a useful size relative to the number
        of blocks and vtds, and matches from shapefile to shapefile)

    inputs:
        :chain_units_path:   shapefile to prorate values INTO
        :data_units_path:    shapefile that has the values to prorate
        :chain_groupby_name: name of column in chain_units_path that matches values in data_units (e.g. "COUNTY")
        :data_groupby_name:  name of column in data_units_path that matches values in chain_units (e.g. "COUNTYFP")
        :prorate_cols:       list of columns to prorate from data_units to chain_units
        :output_file_name:   name of shapefile to output
    """

    #read the files and add unique identifier
    blks = gp.read_file(data_units_path)
    vtds = gp.read_file(chain_units_path)
    vtds['__ID'] = range(len(vtds))
    blks['__ID'] = range(len(blks))

    # get unique values in the common field: chain_groupby_name (or data_groupby_name)
    counties = vtds[chain_groupby_name].unique().tolist()

    # create lookupTable structure to use for prorating
    namelookup = pd.DataFrame({x: {y: 0 for y in prorate_cols}
                               for x in vtds['__ID'].tolist()}).transpose()
    namelookup.index.names = ['large']
    all_lookups = pd.DataFrame({"small":[], "large":[]})

    bnames=["__ID"]+prorate_cols
    # for each value in the unique values, create a lookup
    # for the untis matching that value in both shapefiles.
    for county in counties:
        b = blks.loc[blks[data_groupby_name] == county]
        for name in prorate_cols:
            b[name] = b[name].astype(float)
        v = vtds.loc[vtds[chain_groupby_name] == county]

        l = fasterLookupTable(v, b, '__ID','__ID')
        l = l.merge(b.loc[:, bnames], left_on='small', right_on='__ID')

        all_lookups.update(l.loc[:, ['small','large']])
        amounts = l.groupby('large')[prorate_cols].sum()
        namelookup.update(amounts)

    all_lookups.to_csv("lookupTable.csv")

    namelookup['LG'] = namelookup.index.tolist()
    cs = [x for x in vtds.columns if x not in prorate_cols]
    vtds.loc[:, cs].merge(namelookup, left_on='__ID', right_on='LG').to_file(output_file_name.split('.shp')[0])
    print("FINISHED!!!!")
