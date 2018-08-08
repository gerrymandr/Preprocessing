"""
   Author: Mary Barker

   This code takes a shapefile and makes sure that the geometries 
   do not have units inside units in a donut-style formation. 

   e.g.: 

         |                    |
   ------|--------------------|---------
         |     _______        |
         |    |       |       |
         |    |_______|       |
         |                    |
   ------|--------------------|---------
         |                    |

   main functions:
      :simplify_geometries: reads in shapefile and checks everything as stated

   auxiliary functions:
      :remove_donuts: dissolves units contained inside other units
      :remove_single_neighbors: dissolves units that have a single neighbor into that neighbor
"""
import geopandas as gp
import pysal as ps
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, box, MultiPolygon
from shapely.ops import cascaded_union


def remove_donuts(df, id_col=None):
    """
        takes a GeoDataFrame and dissolves all geometries that are 
        contained completely inside another. e.g.: 

          \              /             \              /
           \------------/               \------------/
           |    _____   |               |            |
           |   / |___|  |               |            |
           |  |   _| |  |   becomes:    |            |
           |   \_|___|  |               |            |
           |            |               |            |
        ---|------------|-           ---|------------|-

    inputs:
        :df: GeoDataFrame to remove donuts from
        :id_col: Unique ID column to use for the dissolving (will make one up else)

    returns:
        :no_donuts_df: GeoDataFrame without the donuts
        :LookupTable: Pandas DataFrame with original geometry ID to new geometry ID's
    """

    if not id_col:
        id_col = "__ID"
        df[id_col] = range(len(df))

    # get neighbors for each vtd by GEOID
    neighbors = ps.weights.Rook.from_dataframe(df, idVariable=id_col).neighbors

    df = df.set_index(id_col)

    # get all vtds into a list and set donuts as the ones that might be problematic
    flagged = set(df.index)
    donuts = [x for x in df.index if 
            (isinstance(df.geometry[x], Polygon) and len(df.geometry[x].interiors) > 0)]

    # go over all potential donut districts and see if there are 
    newdf = []
    OldToNewLookup = {}
    for bigDonut in donuts:
        # check if it's been added already
        if bigDonut in flagged:

            # get this feature's geometry and bounding box
            g1 = df.geometry[bigDonut]
            bbox = box(*g1.bounds)

            # get a list of all of its neighbors and their neighbors
            nbrs = set(neighbors[bigDonut])
            for x in nbrs:
                nbrs = nbrs.union(set(neighbors[x]))
            ngs = [g1]

            # look through its neighbors and see if they're interior
            for nb in nbrs.intersection(flagged):
                if nb != bigDonut:
                    g2 = df.geometry[nb]
                    if bbox.contains(g2):
                        ngs.append(g2)
                        OldToNewLookup[nb] = bigDonut
                        flagged.discard(nb)

            flagged.discard(bigDonut)
            OldToNewLookup[bigDonut] = bigDonut
            newdf.append((bigDonut, cascaded_union(ngs)))

    for x in flagged:
        newdf.append((x, df.geometry[x]))
        OldToNewLookup[x] = x

    OldToNewLookup = pd.DataFrame({
        "originalID": [x for x in OldToNewLookup.keys()],
        "noDonutsID": [x for x in OldToNewLookup.values()]
        })

    newdf = [x for x in zip(*newdf)]
    no_donuts_df = gp.GeoDataFrame({"ID": newdf[0], "geometry": newdf[1]})

    return no_donuts_df, OldToNewLookup


def remove_single_neighbors(df, id_col=None):
    """ 
        Now fixes the problem where units have a single neighbor. 

        E.G.
              _______________                   _______________
             /+++++++++++++++|                 /+++++++++++++++|
            /+++++___ +++++++|   becomes:     /++++++++++++++++| 
           /+++++/####\++++++|               /+++++++++++++++++|
          /+++++/######\+++++|              /++++++++++++++++++|
        =======================           =======================
           exterior boundary               exterior boundary
    """
    if not id_col:
        id_col = "__ID"
        df[id_col] = range(len(df))

    neighbors = ps.weights.Rook.from_dataframe(df, idVariable=id_col).neighbors
    edge_problems = [x for x in neighbors if len(neighbors[x]) == 1]

    df = df.set_index(id_col)
    unvisited_vtds = set(df.index.tolist())
    OldToNewLookup = {"originalID": [], "noDonutsID": []}

    for problem in edge_problems:
        if problem in unvisited_vtds:
            [nbr] = neighbors[problem]
            OldToNewLookup['originalID'].append(problem)
            OldToNewLookup['noDonutsID'].append(nbr)

            g1 = df.geometry[problem]
            g2 = df.geometry[nbr]

            df.loc[nbr, 'geometry'] = g1.union(g2)
            df.drop(problem, inplace=True)
            unvisited_vtds.discard(problem)

    for x in unvisited_vtds:
        OldToNewLookup['originalID'].append(x)
        OldToNewLookup['noDonutsID'].append(x)

    return df, pd.DataFrame(OldToNewLookup)


def simplify_geometries(df=None, shapefile_path=None, output_shapefile_name='no_donuts_vtds'):
    if (df is None) and shapefile_path is not None:
        df = gp.read_file(shapefile_path)
    elif df is None:
        print("simplify_geometries function takes either "+
                "a GeoDataFrame or else a path to a shapefile\naborting")
        return

    ndf,firstLookup = remove_donuts(df)
    intermediate = list(firstLookup['noDonutsID'].unique())
    firstLookup['intermediate'] = [str(intermediate.index(x)) for x in firstLookup['noDonutsID']]

    ndf,secondLookup = remove_single_neighbors(ndf)
    secondLookup['intermediate'] = secondLookup['originalID'].astype(str)

    firstLookup.loc[:, ['originalID','intermediate']].merge(
            secondLookup.loc[:, ['intermediate','noDonutsID']],
            how='outer',
            on='intermediate').to_csv("simplifyGeometriesLookupTable.csv")
    ndf.to_file(output_shapefile_name)
