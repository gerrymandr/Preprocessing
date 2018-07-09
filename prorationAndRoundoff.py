import numpy as np
import pandas as pd
import geopandas as gp


def getLookupTable(largerShapes, smallerShapes, largeIDCol="GEOID10", smallIDCol="GEOID10"):
    """ Creates a datafram with columns that show correspondence between the units
        units in largerShapes geopandas datafram and smallerShapes geopandas dataframe

        Note that this allows smallerShapes to be split across largerShapes, though
        this is not desired in some cases.

    inputs:
        :largerShapes: geopandas dataframe with larger shapes
        :smallerShapes: geopandas dataframe with smaller shapes
        :largeIDCol: string, name of unique identifier for units in largerShapes
        :smallIDCol: string, name of unique identifier for units in smallerShapes

    returns:
        pandas dataframe with each row containing 3 items:
        id of smaller unit, id of larger unit it overlaps with, and area of overlap
    """
    # make unique id for each df
    largerShapes['largeID'] = largerShapes[largeIDCol]
    smallerShapes['smallID'] = smallerShapes[smallIDCol]

    # get lookup of smaller shapes to larger shapes
    smallToLarge = gp.overlay(smallerShapes, largerShapes, how="intersection")
    smallToLarge['area'] = gp.GeoSeries(smallToLarge['geometry']).area

    smallToLarge = pd.DataFrame({'small': smallToLarge['smallID'],
                                 'large': smallToLarge['largeID'],
                                 'area':  smallToLarge['area']})
    return smallToLarge

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

def getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, smallIDCol="GEOID", smallPopCol=None, basicIDCol="GEOID", bigIDCol="GEOID", bigVoteColumn=["votes"]):
    if (smallDF is None) or (smallPopCol is None):
        # if no smaller units specified, then prorate by area of overlap between big and basic units
        smallToBig = fasterLookupTable(largerShapes=bigDF, smallerShapes=basicDF, largeIDCol=bigIDCol, smallIDCol=basicIDCol, by_area=True)
        smallToBig = smallToBig.rename(columns={"large":"bigUnits","small":"basicUnits"})
        smallToBig["pop"] = smallToBig["area"]
        for c in bigVoteColumn:
            smallToBig[c] = [bigDF.loc[bigDF[bigIDCol] == x, c].tolist()[0] for x in smallToBig['bigUnits']]
    else:
        smallToBig = fasterLookupTable(largerShapes=bigDF, smallerShapes=smallDF, largeIDCol=bigIDCol, smallIDCol=smallIDCol)
        smallToBig = smallToBig.rename(columns={"large":"bigUnits"})
        smallToBasic = fasterLookupTable(largerShapes=basicDF, smallerShapes=smallDF, largeIDCol=basicIDCol, smallIDCol=smallIDCol)
        smallToBasic = smallToBasic.rename(columns={"large":"basicUnits"})
        smallToBasic["pop"] = [smallDF.loc[smallDF[smallIDCol] == x, smallPopCol].values[0] for x in smallToBasic["small"]]
        for c in bigVoteColumn:
            smallToBig[c] = [bigDF.loc[bigDF[bigIDCol] == x, c].tolist()[0] for x in smallToBig['bigUnits']]

        cols = ['bigUnits','small']
        cols.extend(bigVoteColumn)
        smallToBig = smallToBig.loc[:,cols].merge(smallToBasic)
    return smallToBig

def prorateWithDFs(bigDF, basicDF, smallDF=None, bigIDCol="GEOID", basicIDCol="GEOID", smallIDCol=None, smallPopCol=None, bigVoteColumns=["VoteCount"], myData=None):
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

    if myData is None:
        if (smallDF is None) or (smallPopCol is None):
            # if no smaller units specified, then prorate by area of overlap between big and basic units
            smallToBig = fasterLookupTable(bigDF, basicDF, bigIDCol, basicIDCol, by_area=True)
            smallToBig = smallToBig.rename(columns={"large":"bigUnits","small":"basicUnits"})
            for c in bigVoteColumns:
                smallToBig[c] = [bigDF.loc[bigDF[bigIDCol] == x, c].tolist()[0] for x in smallToBig['bigUnits']]
            myData = smallToBig

        else:
            smallToBig = fasterLookupTable(bigDF, smallDF, bigIDCol, smallIDCol)
            smallToBig = smallToBig.rename(columns={"large":"bigUnits"})
            smallToBasic = fasterLookupTable(basicDF, smallDF, basicIDCol, smallIDCol)
            smallToBasic = smallToBasic.rename(columns={"large":"basicUnits"})

            for c in bigVoteColumns:
                smallToBig[c] = [bigDF.loc[bigDF[bigIDCol] == x, c].tolist()[0] for x in smallToBig['bigUnits']]
            cols = [x for x in bigVoteColumns]
            cols.extend(["bigUnits", "small"])
            myData = smallToBig.loc[:,cols].merge(smallToBasic)
    else:
        if smallPopCol:
            for c in bigVoteColumns:
                myData[c] = [bigDF.loc[bigDF[bigIDCol] == x, c].tolist()[0] for x in myData['bigUnits']]

    columns = [x for x in bigVoteColumns]
    columns.extend([smallIDCol or 'pop', 'area'])

    myData = myData.groupby(["basicUnits", "bigUnits"])[columns].sum()
    [small, big] = list(zip(*myData.index.tolist()))
    area =  np.array(myData['area'].tolist())
    pops =  np.array(myData['pop'].tolist())
    votes = [np.array(myData[c].tolist()) for c in bigVoteColumns]
    votes = [x * pops for x in votes]

    myData = pd.DataFrame({"ID":small, "area":area, "pop": pops})
    for i, x in enumerate(bigVoteColumns):
        myData[x] = votes[i]
    myData = myData.groupby(["ID"])[columns].sum()
    for c in bigVoteColumns:
        myData[c] /= myData['pop']

    return dict(zip(myData.index, zip(*[myData[c] for c in bigVoteColumns])))


def roundoffWithDFs(basicDF, bigDF, smallDF=None, basicID=None, bigID=None, smallID=None, smallPopCol=None, lookup=None):
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

    if lookup is None:
        if smallDF is not None:
            smallToBig = fasterLookupTable(largerShapes=bigDF, smallerSHapes=smallDF, largeIDCol=bigID, smallIDCol=smallID)["large","small"]
            smallToBasic = fasterLookupTable(basicDF, smallDF, basicID, smallID).rename(columns={"large":"basicUnits"})
            lookup = smallToBig.merge(smallToBasic).rename(columns={"large":"bigUnits"})
        else:
            lookup = fasterLookupTable(largerShapes=bigDF, smallerShapes=basicDF, largeIDCol=bigID, smallIDCol=basicID, by_area=True).rename(columns={'small':"basicUnits","large":"bigUnits"})

    lookup['pop'] = lookup['area']
    if smallPopCol:
        smallDF[smallID] = smallDF[smallID].astype(str)
        lookup['pop'] = [smallDF.loc[smallDF[smallID] == str(x), smallPopCol].tolist()[0] for x in lookup['small']]

    basicToBigLookup = lookup.groupby(["basicUnits", "bigUnits"])["pop"].sum()

    correspondence = {}
    for unit in basicDF[basicID]: 
        maxArea = max(basicToBigLookup[unit])
        bigID = basicToBigLookup.loc[basicToBigLookup == maxArea].index[0]
        correspondence[unit] = bigID[1]
    return correspondence

