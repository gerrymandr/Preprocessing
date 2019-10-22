"""
   Author: Mary Barker

   This code takes an existing shapefile and checks that its geographic units 
   overlap 'nicely'. i.e.: border each other without gaps or overlap.


   main functions:
      :check_shapefile_connectivity: reads in shapefile and checks everything as stated

   auxiliary functions:
      :check_for_holes: checks if there are any gaps between polygons that might be considered neighbors.

      :check_for_overlap: checks if two geometries overlap in a polygon with nonzero area.

      :get_nbr_by_longest_perim: takes arbitrary Polygon P and GeoDataFrame F, and
                      finds the geometry in F that shares the most boundary with P
"""
import geopandas as gp
from shapely.geometry import Polygon,MultiPolygon
import pysal as ps
import os


def check_for_holes(gdf):
    """
    inputs:
        :gdf: GeoDataFrame (fiona) that needs to be checked for holes
    returns:
        :holes: a (possibly empty) list of the holes not filled in by geometries
    """
    entire_geom = gdf.geometry.unary_union

    if type(entire_geom) == MultiPolygon:
        return [Polygon(list(x.coords)) for p in entire_geom.geoms for x in p.interiors]

    elif type(entire_geom) == Polygon:
        return [Polygon(list(x.coords)) for x in entire_geom.interiors]


def check_for_overlap(gdf, adj="Queen"):
    """
    inputs: 
      :gdf: GeoDataFrame (fiona-style) to check overlapping geometries for
      :adj: ( Queen/queen/Q/q, Rook/rook/R/r ) type of adjacency to check

    returns: 
      :overlaps: (possibly empty) dictionary with offending overlaps structured as:
          * key:   tuple(id1, id2) where id1, id2 geometries intersect in a polygon
          * value: geometry of their intersection
    """
    overlaps = {}
    if "q" in adj.lower():
        neighbors = ps.weights.Queen.from_dataframe(gdf, geom_col="geometry").neighbors
    elif "r" in adj.lower():
        neighbors = ps.weights.Rook.from_dataframe(gdf, geom_col="geometry").neighbors

    for nb1 in neighbors:
        for nb2 in neighbors[nb1]:
            g = gdf.geometry[nb1].intersection(gdf.geometry[nb2])
            if g.area > 0:
                overlaps[(nb1,nb2)] = g
    return overlaps


def get_nbr_by_longest_perim(gdf, polys):
    """
    inputs:
        :polys: list of polygons to find nice neighbors for
    returns:
        :nbrs: list of neighbor indices to associate to polys
    """
    print([])
    inters = [ [(i, poly, poly.intersection(x).length) for i, x in
                zip(gdf.index.tolist(), gdf.geometry) if poly.intersects(x)] for poly in polys]
    return [sorted(x, key=lambda y: y[2])[0] for x in inters]


def check_shapefile_connectivity(dataframe=None, shapefile_path=None, adj="Queen", output_name="connectivity_better"):
    if (dataframe is None) and shapefile_path:
        try:
            dataframe = gp.read_file(shapefile_path)
        except:
            print("ERROR: could not read file. this needs either a shapefile or a GeoDataFrame")
            return
    if dataframe is None:
        print("check_shapefile_connectivity takes a dataframe or a shapefile_path argument")
        return

    dataframe.index = range(len(dataframe))

    print("checking for holes....")
    holes = check_for_holes(dataframe)
    if len(holes) > 0:
        print(f"WARNING: {len(holes)} holes detected in shapefile.\nauto-fixing...")
        nbrs = get_nbr_by_longest_perim(dataframe, holes)
        for nb in nbrs:
            rowid = nb[0]
            poly = nb[1]
            g = dataframe.geometry[rowid]
            dataframe.geometry[rowid] = g.union(poly)


    print("checking for overlapping geometries....")
    overlaps = check_for_overlap(dataframe, adj=adj)
    if len(overlaps) > 0:
        print(f"WARNING: {len(overlaps)} non-trivial overlaps detected in shapefile.\nauto-fixing...")

        for overlap in overlaps:
            (unit1, unit2) = overlap
            g1 = dataframe.geometry[unit1]
            g2 = dataframe.geometry[unit2]

            dataframe.geometry[unit1] = g1.difference(g2)

    dataframe.to_file(output_name.split('.shp')[0])
