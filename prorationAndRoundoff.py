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


def getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, smallIDCol="GEOID", smallPopCol=None, basicIDCol="GEOID", bigIDCol="GEOID"):
    if (smallDF is None) or (smallPopCol is None):
        # if no smaller units specified, then prorate by area of overlap between big and basic units
        smallToBig = fasterLookupTable(largerShapes=bigDF, smallerShapes=basicDF, largeIDCol=bigIDCol, smallIDCol=basicIDCol, by_area=True)
        smallToBig = smallToBig.rename(columns={"large":"bigUnits","small":"basicUnits"})
        smallToBig["pop"] = smallToBig["area"]
    else:
        smallToBig = fasterLookupTable(largerShapes=bigDF, smallerShapes=smallDF, largeIDCol=bigIDCol, smallIDCol=smallIDCol)
        smallToBig = smallToBig.rename(columns={"large":"bigUnits"})
        smallToBasic = fasterLookupTable(largerShapes=basicDF, smallerShapes=smallDF, largeIDCol=basicIDCol, smallIDCol=smallIDCol)
        smallToBasic = smallToBasic.rename(columns={"large":"basicUnits"})
        smallToBasic["pop"] = [smallDF.loc[smallDF[smallIDCol] == x, smallPopCol].values[0] for x in smallToBasic["small"]]
        cols = ['bigUnits','small']
        smallToBig = smallToBig.loc[:,cols].merge(smallToBasic)
    return smallToBig


def prorateWithDFs(bigDF, basicDF, bigIDCol="GEOID", basicIDCol="GEOID", bigVoteColumns=[], myData=None, prorateCol='area'):
    """ Takes 3 geopandas dataframes in order of inclusion, where biggerUnitsData
        has some data saved in columns (in dataCols) that needs to be prorated down
        to basic units either by intersection area (area) or else
        by some other attribute (e.g. population)

    inputs:
        :bigDF: geopandas dataframe of largest units
        :basicDF:  geopandas dataframe
        :smallDF:  geopandas dataframe
        :myData: pandas dataframe of overlap correspondence (if any) with area and vote allocation
    """

    # NOTE: 'area' in this context means either land area or else population.
    # since we are assigning values from one district to another based on a
    # definition of overlap that is either area of land or else the proportion
    # of population in the overlap, I chose a name that relates to one of these

    bigDF['totalAmounts'] = [myData.loc[myData['bigUnits'] == x, prorateCol].sum() for x in bigDF[bigIDCol]]
    myData = myData.merge(bigDF.loc[:, [bigIDCol, 'totalAmounts', *bigVoteColumns]], left_on='bigUnits', right_on=bigIDCol,  how='outer')

    for c in bigVoteColumns:
        myData[c] = myData[c].astype(float) * myData[prorateCol].astype(float) / myData['totalAmounts'].astype(float)

    myData = myData.groupby(["basicUnits"])[bigVoteColumns].sum()

    return dict(zip(myData.index, zip(*[myData[c] for c in bigVoteColumns])))


def roundoffWithDFs(basicDF, bigDF, smallDF=None, basicID=None, bigID=None, smallID=None, smallPopCol=None, lookup=None, prorateCol='pop'):
    """ Create lookup table that assigns each basicDF unit to a bigDF unit
        based on either area of overlap (if smallDF or smallPopCol is not valid)
        or else based on the value of smallDF units that are inside the overlap of given
        bigDF and basicDF units.

    inputs:
        :basicDF: geopandas dataframe of basic units
        :bigDF: geopandas dataframe of big units
        :smallDF: geopandas dataframe of small units
        :basicID: name of column of unique id for basic Units
        :bigID: name of column of unique id for big Units
        :smallID: name of column of unique id for small Units
        :smallPopCol: name of column for small units population
        :lookup: pandas dataframe of overlap correspondence (if any)
    output:
        pandas dataframe of basicDF IDs and corresponding bigDF IDs
    """


    correspondence = {}
    roundedUnits = set(lookup['basicUnits'].tolist())
    for unit in basicDF[basicID]: 
        if unit in roundedUnits:
            maxArea = lookup['bigUnits'][lookup.loc[lookup['basicUnits'] == unit, 'pop'].idxmax()]
        correspondence[unit] = maxArea
    return correspondence

