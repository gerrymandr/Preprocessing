import geopandas as gp
import numpy as np
import pandas as pd
import pysal as ps

from math import pi
from shapely.geometry.multipolygon import MultiPolygon

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

"""
for cleaning up later: 
import reportlab.platypus as rps

def insert_vals(text, style, bulletText=None):
    value =  getattr(rps, text[0])
    return value(*text[1])

can then insert values as 
Story.append(Spacer(1,10))
Story.append(insert_vals(["Paragraph",['''nothing at all''', styleN]], 'a'))
Story.append(Spacer(1,10))
"""

# Basic report on a given shapefile
def generic_shapefile_report(
            reportfilename="basic_report_file_",
            dataframe = None,
            filename = None,
            idcolumn = None,
            popcolumn = None,
            votecolumns = None,
            demographiccolumns = None,
            printcolumns = True
        ):

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH1 = styles['Heading1']
    styleH2 = styles['Heading2']
    styleB = styles['Bullet']
    texts = []
    styles = []

    if filename:
        # 0 Get basic attributes of the datafile to be reported
        if dataframe is None:
            dataframe = gp.read_file(filename)
        myfname = filename.split('/')[-1]
        numUnits = len(dataframe)
        numMultiUnits = sum([1 for x in dataframe["geometry"] if type(x) == MultiPolygon])
        neighbors = ps.weights.Rook.from_dataframe(dataframe, geom_col="geometry").neighbors
        numNbrs = np.array([float(len(x)) for x in neighbors.values()])
        avgNbrs, maxNbrs, minNbrs = np.mean(numNbrs), max(numNbrs), min(numNbrs)

        numUnitsInsideUnits = sum([1 for x in neighbors.keys() if len(neighbors[x]) == 1])
        numIslands = sum([1 for x in neighbors.keys() if len(neighbors[x]) == 0])
        areas = np.array([float(x.area) for x in dataframe["geometry"]])
        perims = np.array([float(x.length) for x in dataframe["geometry"]])
        maxArea, minArea, avgArea = max(areas), min(areas), np.mean(areas)
        maxPerim, minPerim, avgPerim = max(perims), min(perims), np.mean(perims)
        polsbyPopper = 4.0 * pi * areas / (perims**2)
        avgPolsPop, maxPolsPop, minPolsPop = np.mean(polsbyPopper), max(polsbyPopper), min(polsbyPopper)

        # 1 Title
        texts.append(["paragraph", f""" <h1> Overview of {myfname} </h1> """])
        styles.append([styleH1])
        texts.append(["spacer", (1,5)])
        styles.append([])

        # 2 Dataframe overview: 

        # 2.0 column names
        if printcolumns:
            texts.append(["paragraph", """column names: {}""".format(", ".join(dataframe.columns))])
            styles.append([styleN])
            texts.append(["spaceer", (1,5)])
            styles.append([])

        # 2.1 geometry
        texts.append(["paragraph",f"""<h2> Geometry of units </h2>"""])
        styles.append([styleH2])
        texts.append(["paragraph",f"""Number of units: {numUnits}"""])
        styles.append([styleN])
        texts.append(["paragraph", f"""Number of disconnected units: {numIslands} """])
        styles.append([styleN, 'o'])
        texts.append(["paragraph", f"""Number of multiply connected or island-containing units: {numMultiUnits} """])
        styles.append([styleN, 'o'])
        texts.append(["paragraph", f"""Number of units contained completely inside another: {numUnitsInsideUnits} """])
        styles.append([styleN, 'o'])
        texts.append(["paragraph", f"""Average number of neighbors: {avgNbrs}"""])
        styles.append([styleN, 'o'])
        texts.append(["paragraph", f"""Highest degree of connectivity: {maxNbrs}"""])
        styles.append([styleN, 'o'])
        texts.append(["paragraph", f"""Average, maximum, and minimum Polsby-Popper scores: {avgPolsPop}, {maxPolsPop}, {minPolsPop}"""])
        styles.append([styleN, 'o'])
        texts.append(["paragraph", f"""Average area of units: {avgArea}, Average Perimeter of units: {avgPerim}"""])
        styles.append([styleN, 'o'])
        texts.append(["paragraph", f"""Maximum & Minimum area of units: {maxArea}, {minArea}"""])
        styles.append([styleN, 'o'])
        texts.append(["paragraph", f"""Maximum & Minimum Perimeter of units: {maxPerim}, {minPerim}"""])
        styles.append([styleN, 'o'])
        texts.append(["spacer", (1,12)])
        styles.append([])

        # 2.2 particular columns
        if idcolumn or popcolumn or (votecolumns is not None) or (demographiccolumns is not None):
            texts.append(["paragraph",f"""<h2> Column data </h2>"""]) 
            styles.append([styleH2])
            if idcolumn:
                numUniqueIds = len(set(dataframe[idcolumn].tolist()))
                texts.append(["paragraph", f"""ID column: {idcolumn} has {numUniqueIds} unique elements. """])
                styles.append([styleN])
                if numUniqueIds != numUnits:
                    texts.append(["paragraph","""<h2> Warning: ID column not unique! At least 2 units have the same ID </h2>"""])
                    styles.append([styleH2])
            if popcolumn:
                pops = np.array(dataframe[popcolumn].tolist())
                totPops = sum(pops)
                maxPops, minPops, avgPops, numZero = max(pops), min(pops), np.mean(pops), sum(pops == 0)
                texts.append(["paragraph", f"""Total population reprted: {totPops}"""])
                styles.append([styleN])
                texts.append(["paragraph", f"""Maximum population by unit: {maxPops}"""])
                styles.append([styleN, 'o'])
                texts.append(["paragraph", f"""Minimum population by unit: {minPops}"""])
                styles.append([styleN, 'o'])
                texts.append(["paragraph", f"""Average population per unit: {avgPops}"""])
                styles.append([styleN, 'o'])
                texts.append(["paragraph", f"""Number of units with 0 population:  {numZero}"""])
                styles.append([styleN, 'o'])

            if votecolumns is not None:
                vcols = ", ".join(votecolumns)
                ncols = len(votecolumns)
                texts.append(["spacer", (1,5)])
                styles.append([])
                texts.append(["paragraph", """<h2> Election Data </h2>"""])
                styles.append([styleH2])
                texts.append(["paragraph", f"""Reported values in columns: {vcols}"""])
                styles.append([styleN])
                texts.append(["spacer", (1,5)])
                styles.append([])
                vdata = [["column name", "Max", "Min", "Average", "Variance"]]
                for col in votecolumns:
                    votes = np.array(dataframe[col].tolist())
                    maxv, minv, avgv, varv = max(votes), min(votes), np.mean(votes), np.var(votes)
                    vdata.append([col, maxv, minv, avgv, varv])
                texts.append(["table", (vdata, 5*[inch], (ncols+1)*[0.4*inch])])
                styles.append([
                [('ALIGN',(1,1),(-2,-2),'RIGHT'),
                ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                ('TEXTCOLOR',(0,0),(-1,0),colors.blue),
                ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                ('INNERGRID', (0,0), (4,ncols), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black)]
                ])
                texts.append(["spacer", (1,5)])
                styles.append([])

            if demographiccolumns is not None:
                dcols = ", ".join(demographiccolumns)
                ncols = len(demographiccolumns)
                texts.append(["spacer", (1,5)])
                styles.append([])
                texts.append(["paragraph", """<h2> Demographic Data </h2>"""])
                styles.append([styleH2])
                texts.append(["paragraph", f"""Reported values in columns: {dcols}"""])
                styles.append([styleN])
                texts.append(["spacer", (1,5)])
                styles.append([])
                ddata = [["column name", "Max", "Min", "Average", "Variance"]]
                for col in demographiccolumns:
                    votes = np.array(dataframe[col].tolist())
                    maxv, minv, avgv, varv = max(votes), min(votes), np.mean(votes), np.var(votes)
                    ddata.append([col, maxv, minv, avgv, varv])
                texts.append(["table", (ddata, 5*[inch], (ncols+1)*[0.4*inch])])
                styles.append([
                [('ALIGN',(1,1),(-2,-2),'RIGHT'),
                ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                ('TEXTCOLOR',(0,0),(-1,0),colors.blue),
                ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                ('INNERGRID', (0,0), (4,ncols), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black)]
                ])
                texts.append(["spacer", (1,5)])
                styles.append([])

        texts.append(["spacer", (1,12)])
        styles.append([])
        # write report to file
        if reportfilename is not None:
            if reportfilename == "basic_report_file_":
                reportfilename += myfname+".pdf"
            doc = SimpleDocTemplate(reportfilename, pagesize=letter) 
            #doc.build(Story)
    return texts, styles

# PRORATION AND ROUNDOFF REPORT
def prorate_and_roundoff_report(
        reportOutputFileName="ProrateAndRoundoff.pdf",
        biggerUnits=None,
        basicUnits=None,
        smallestUnits=None,
        big_geoid=None,
        basic_geoid=None,
        small_geoid=None,
        population=None,
        votes=None,
        lookupTable=None):

    # Process the 3 datafiles and their differences in geometry
    popcol = population != ''
    bigdf = biggerUnits.split('/')[-1]
    basicdf = basicUnits.split('/')[-1]
    bigDF = gp.read_file(biggerUnits)
    basicDF = gp.read_file(basicUnits)
    smalldf = ''
    smallDF = None

    if smallestUnits:
        smalldf = smallestUnits.split('/')[-1]
        smallDF = gp.read_file(smallestUnits)
    pop = population
    nbasic = len(basicDF)
    nbig = len(bigDF)

    # get all of the units in basicDF that have multiple bigDF entries 
    # that correspond to it(i.e. the ones that are split by bigDF units)
    basicsplit = [x for x in lookupTable["basicUnits"].unique() if len(lookupTable.loc[lookupTable["basicUnits"]== x, :]) > 1]

    # get the average number of pieces each of the split basicUnits is in
    avgNumOfSplits = len(lookupTable.loc[lookupTable["basicUnits"].isin(basicsplit), "bigUnits"]) * 1.0 / len(basicsplit)

    # get area of each piece 
    splitOnes = lookupTable.loc[ lookupTable['basicUnits'].isin(basicsplit), ["area", "basicUnits"]]
    basicsplit = splitOnes["basicUnits"].tolist()

    intersectArea = np.array(splitOnes['area'].tolist())
    basicsplitsize = [basicDF.loc[basicDF[basic_geoid] == x, "geometry"] for x in basicsplit]
    areas = [float(x.area) for x in basicsplitsize]
    basicSplitProportion = np.max(abs(intersectArea / areas - 0.5))
    bigsplitsize=1# = np.max(abs(intersectArea / areas - 0.5))

    nbasicsplit = len(set(basicsplit))

    doc = SimpleDocTemplate(reportOutputFileName, pagesize=letter) 
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH1 = styles['Heading1']
    styleH2 = styles['Heading2']
    styleB = styles['Bullet']
    Story=[]


    Story.append(Paragraph(f""" <h1> Assigning units in {bigdf} to {basicdf} </h1> """, styleH1))
    Story.append(Spacer(1,5))
    Story.append(Paragraph("""<h2> Assignment type: </h2> """, styleH2))
    if popcol:
        Story.append(Paragraph("the assignment was done in terms of the "+str(pop)+" column in "+str(smalldf), styleN))
    else:
        Story.append(Paragraph("since no smaller geographic units were specified, the assignment was done based on area", styleN))

    Story.append(Spacer(1,12))

    Story.append(Paragraph(f"""<h2> File: {basicdf} </h2> """, styleH2))
    Story.append(Paragraph(f"""total number of {basicdf} units: {nbasic}  """, styleN))

    Story.append(Paragraph(f"""<h2> File: {bigdf} </h2> """, styleH2))
    Story.append(Paragraph(f""" total number of {bigdf} units: {nbig}""", styleN))


    Story.append(Spacer(1,12))
    Story.append(Paragraph(f"""<h2> Distance between {basicdf} and {bigdf} </h2> """, styleH2))
    ptext = f"""number of {basicdf} units split by assignment: {nbasicsplit} """ 
    Story.append(Paragraph(ptext, styleN, bulletText='o'))
    Story.append(Spacer(1,5))
    ptext = f"""average proportional size of split for {basicdf} units:  {basicSplitProportion} """
    Story.append(Paragraph(ptext, styleN, bulletText='o'))
    Story.append(Spacer(1,5))
    ptext = f"""average proportional size of split for {bigdf} units:  {bigsplitsize} """
    Story.append(Paragraph(ptext, styleN, bulletText='o'))

    for index, value in enumerate([(bigdf, big_geoid), (basicdf, basic_geoid), (smalldf, small_geoid)]):
        filename, geoid = value
        if filename == bigdf:
            votes = ['votes']
        elif filename != bigdf:
            votes = None

        if filename is not None:
            ts, ss = generic_shapefile_report(
                    reportfilename=None, 
                    filename = filename, 
                    idcolumn = geoid,
                    votecolumns = votes,
                    printcolumns = True)
            Story.append(Spacer(1,12))
            for t, s in zip(ts, ss):
                if t[0] == "paragraph":
                    if len(s) > 1:
                        Story.append(Paragraph(t[1], s[0], bulletText=s[1]))
                    else:
                        Story.append(Paragraph(t[1], s[0]))
                elif t[0] == "spacer":
                    Story.append(Spacer(*t[1]))
                elif t[0] == "table":
                    if filename == bigdf:
                        myt=Table(*t[1])
                        myt.setStyle(TableStyle(s[0]))
                        Story.append(myt)
    doc.build(Story)


def multifile_report(reportOutputFileName, list_of_inputs):
    """
        [ [biggerUnits, big_geoid, []],
            [basicUnits, basic_geoid, []],
            [smallestUnits, small_geoid]])
    """

    doc = SimpleDocTemplate(reportOutputFileName, pagesize=letter) 
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH1 = styles['Heading1']
    styleH2 = styles['Heading2']
    styleB = styles['Bullet']
    Story=[]

    Story.append(Paragraph("""<h1>Initial File Report On Multiple Files</h1>""", styleH1))
    Story.append(Spacer(1,20))

    for inputs in list_of_inputs:
        dfname = inputs[0]
        geoid = inputs[1]

        ts, ss = generic_shapefile_report(
                reportfilename=None, 
                filename = dfname, 
                idcolumn = geoid,
                printcolumns = True)
        Story.append(Spacer(1,12))

        for t, s in zip(ts, ss):
            if t[0] == "paragraph":
                if len(s) > 1:
                    Story.append(Paragraph(t[1], s[0], bulletText=s[1]))
                else:
                    Story.append(Paragraph(t[1], s[0]))
            elif t[0] == "spacer":
                Story.append(Spacer(*t[1]))
   
    doc.build(Story)
    print(f"""Wrote report to file {reportOutputFileName}""")

