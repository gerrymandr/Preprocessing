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
roundTol = 3

def ReportMaxMinAvgVarTotNumZero(Story, liststyles, column=None, dataframe=None, columname=None, variance=False, total=False, numZero=False):
    styles = getSampleStyleSheet()
    if (column is None) and (dataframe is not None):
        column = np.array(dataframe[columname].tolist())
    column = np.array(column)
    values = {"max": max(column), "min": min(column),\
            "avg": np.round(np.mean(column), roundTol), "var": np.round(np.var(column), roundTol) if variance else None,\
            "total": sum(column) if total else None, "numZero": sum(column==0) if numZero else None}
    Story.append(Paragraph(f"""Statistics on  {columname}:"""), style=styles['Normal'])

    for key, val in values.items():
        if val is not None:
            Story.append(Paragraph(f"""{key}: {value}""", *liststyles ))
     

# Basic report on a given shapefile
def generic_shapefile_report(
            reportfilename="basic_report_file_",
            dataframe = None,
            filename = None,
            idcolumn = None,
            popcolumn = None,
            votecolumns = None,
            demographiccolumns = None,
            printcolumns = True, 
            Story=None
        ):

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH1 = styles['Heading1']
    styleH2 = styles['Heading2']
    styleB = styles['Bullet']
    if Story is None:
        Story = []

    if filename:
        # 0 Get basic attributes of the datafile to be reported
        if dataframe is None:
            dataframe = gp.read_file(filename)
        myfname = filename.split('/')[-1]
        numUnits = len(dataframe)
        numMultiUnits = sum([1 for x in dataframe["geometry"] if type(x) == MultiPolygon])
        neighbors = ps.weights.Rook.from_dataframe(dataframe, geom_col="geometry").neighbors
        numNbrs = np.array([float(len(x)) for x in neighbors.values()])
        avgNbrs, maxNbrs, minNbrs = np.round(np.mean(numNbrs), roundTol), max(numNbrs), min(numNbrs)

        numUnitsInsideUnits = sum([1 for x in neighbors.keys() if len(neighbors[x]) == 1])
        numIslands = sum([1 for x in neighbors.keys() if len(neighbors[x]) == 0])
        areas = np.round(np.array([float(x.area) for x in dataframe["geometry"]]), roundTol)
        perims = np.round(np.array([float(x.length) for x in dataframe["geometry"]]), roundTol)
        maxArea, minArea, avgArea = max(areas), min(areas), np.round(np.mean(areas), roundTol)
        maxPerim, minPerim, avgPerim = max(perims), min(perims), np.round(np.mean(perims), roundTol)
        polsbyPopper = np.round(4.0 * pi * areas / (perims**2), roundTol)
        avgPolsPop, maxPolsPop, minPolsPop = np.round(np.mean(polsbyPopper), roundTol), max(polsbyPopper), min(polsbyPopper)

        # 1 Title
        Story.append(Paragraph(f"""<h1> Overview of {myfname} </h1>""", styleH1))
        Story.append(Spacer(1,5))

        # 2 Dataframe overview: 

        # 2.0 column names
        if printcolumns:
            Story.append(Paragraph("""Column names: {}""".format(", ".join(dataframe.columns)), styleN))
            Story.append(Spacer(1,5))

        # 2.1 geometry
        Story.append(Paragraph(f"""<h2> Geometry of units </h2>""", styleH2))
        Story.append(Paragraph(f"""Number of units: {numUnits}""", styleN, bulletText='o'))
        Story.append(Paragraph(f"""Number of disconnected units: {numIslands} """, styleN, bulletText='o'))
        Story.append(Paragraph(f"""Number of multiply connected or island-containing units: {numMultiUnits} """, styleN, bulletText='o'))
        Story.append(Paragraph(f"""Number of units contained completely inside another: {numUnitsInsideUnits} """, styleN, bulletText='o'))
        Story.append(Paragraph(f"""Average number of neighbors: {avgNbrs}""", styleN, bulletText='o'))
        Story.append(Paragraph(f"""Highest degree of connectivity: {maxNbrs}""", styleN, bulletText='o'))
        Story.append(Paragraph(f"""Average, maximum, and minimum Polsby-Popper scores: {avgPolsPop}, {maxPolsPop}, {minPolsPop}""", styleN, bulletText='o'))
        Story.append(Paragraph(f"""Average area of units: {avgArea}, Average Perimeter of units: {avgPerim}""", styleN, bulletText='o'))
        Story.append(Paragraph(f"""Maximum & Minimum area of units: {maxArea}, {minArea}""", styleN, bulletText='o'))
        Story.append(Paragraph(f"""Maximum & Minimum Perimeter of units: {maxPerim}, {minPerim}""", styleN, bulletText='o'))
        Story.append(Spacer(1,12))

        # 2.2 particular columns
        if idcolumn or popcolumn or (votecolumns is not None) or (demographiccolumns is not None):
            Story.append(Paragraph(f"""<h2> Column data </h2>""", styleH2))
            if idcolumn:
                numUniqueIds = len(set(dataframe[idcolumn].tolist()))
                Story.append(Paragraph(f"""ID column: {idcolumn} has {numUniqueIds} unique elements. """, styleN))
                if numUniqueIds != numUnits:
                    Story.append(Paragraph("""<h2> Warning: ID column not unique! At least 2 units have the same ID </h2>""", styleH2))
            if popcolumn:
                pops = np.array(dataframe[popcolumn].tolist())
                totPops = sum(pops)
                maxPops, minPops, avgPops, numZero = max(pops), min(pops), np.round(np.mean(pops), roundTol), sum(pops == 0)
                Story.append(Paragraph(f"""Total population reprted: {totPops}""", styleN))
                Story.append(Paragraph(f"""Maximum population by unit: {maxPops}""", styleN, bulletText='o'))
                Story.append(Paragraph(f"""Minimum population by unit: {minPops}""", styleN, bulletText='o'))
                Story.append(Paragraph(f"""Average population per unit: {avgPops}""", styleN, bulletText='o'))
                Story.append(Paragraph(f"""Number of units with 0 population:  {numZero}""", styleN, bulletText='o'))
                Story.append(Spacer(1,5))

            if votecolumns is not None:
                vcols = ", ".join(votecolumns)
                ncols = len(votecolumns)
                Story.append(Spacer(1,5)) 
                Story.append(Paragraph("""<h2> Election Data </h2>""", styleH2))
                Story.append(Paragraph(f"""Reported values in columns: {vcols}""", styleN))
                Story.append(Spacer(1,5)) 
                vdata = [["column name", "Max", "Min", "Average", "Variance"]]
                for col in votecolumns:
                    votes = np.array(dataframe[col].tolist())
                    maxv, minv, avgv, varv = max(votes), min(votes), np.mean(votes), np.var(votes)
                    vdata.append(
                            [col, np.round(maxv, roundTol),
                            np.round(minv, roundTol), np.round(avgv, roundTol),
                            np.round(varv, roundTol)])
                t=Table(vdata, 5*[inch], (ncols+1)*[0.4*inch])
                t.setStyle(TableStyle([
                ('ALIGN',(1,1),(-2,-2),'CENTER'),
                ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                ('TEXTCOLOR',(0,0),(-1,0),colors.blue),
                ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                ('INNERGRID', (0,0), (4,ncols), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                ]))
                Story.append(t)
                Story.append(Spacer(1,5))

            if demographiccolumns is not None:
                dcols = ", ".join(demographiccolumns)
                ncols = len(demographiccolumns)
                Story.append(Spacer(1,5))
                Story.append(Paragraph("""<h2> Demographic Data </h2>""", styleH2))
                Story.append(Paragraph(f"""Reported values in columns: {dcols}""", styleN))
                Story.append(Spacer(1,5))
                ddata = [["column name", "Max", "Min", "Average", "Variance"]]
                for col in demographiccolumns:
                    votes = np.array(dataframe[col].tolist())
                    maxv, minv, avgv, varv = max(votes), min(votes), np.mean(votes), np.var(votes)
                    ddata.append(
                            [col, np.round(maxv, roundTol),
                            np.round(minv, roundTol), np.round(avgv, roundTol),
                            np.round(varv, roundTol)])
                t=Table(ddata, 5*[inch], (ncols+1)*[0.4*inch])
                t.setStyle(TableStyle([
                ('ALIGN',(1,1),(-2,-2),'CENTER'),
                ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                ('TEXTCOLOR',(0,0),(-1,0),colors.blue),
                ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                ('INNERGRID', (0,0), (4,ncols), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black)
                ]))
                Story.append(t)
                Story.append(Spacer(1,5))

        Story.append(Spacer(1,12))

        # write report to file
        if reportfilename is not None:
            if reportfilename == "basic_report_file_":
                reportfilename += myfname+".pdf"
            doc = SimpleDocTemplate(reportfilename, pagesize=letter) 


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
        prorated=False,
        rounded=False,
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

    basicSplitProportion = np.max(abs(intersectArea / areas))
    bigsplitsize=1# = np.max(abs(intersectArea / areas - 0.5))

    nbasicsplit = len(set(basicsplit))

    doc = SimpleDocTemplate(reportOutputFileName, pagesize=letter) 
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH1 = styles['Heading1']
    styleH2 = styles['Heading2']
    styleB = styles['Bullet']
    Story=[]

    if prorated:
        Story.append(Paragraph(f""" <h1>Proration: {bigdf} to {basicdf}</h1>""", styleH1))
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

    if rounded:
        Story.append(Paragraph(f""" <h1> Roundoff: {bigdf} to {basicdf} </h1> """, styleH1))
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
        Story.append(Spacer(1,20))


    multifile_report(Story=Story, 
            list_of_inputs=[
                {"filename":basicdf, "idcolumn":basic_geoid, "votecolumns":bvotes, "printcolumns":True}, 
                {"filename":bigdf, "idcolumn":big_geoid, "votecolumns":votes, "printcolumns":True}, 
                {"filename":smalldf, "idcolumn":small_geoid, "popcolumn":population, "printcolumns":True}
                ]
            )
    doc.build(Story)
    print(f"""wrote report to file: {reportOutputFileName}""")


def multifile_report(reportOutputFileName=None, list_of_inputs=[], Story=None):
    """Creates a report on multiple shapefiles using the 
    generic_shapefile_report function for each. 

    :inputs: 
    :reportOutputFileName: filename to write to 
    :list_of_inputs: list of dicts each of which acts as **kwargs to generic_shapefile_report
    :Story: if this function is being called from another report generator
    """

    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH1 = styles['Heading1']
    styleH2 = styles['Heading2']
    styleB = styles['Bullet']

    if Story is None:
        Story=[]

    Story.append(Paragraph("""<h1>Initial File Report On Multiple Files</h1>""", styleH1))
    Story.append(Spacer(1,20))

    for inputs in list_of_inputs:
        generic_shapefile_report(
                Story=Story,
                reportfilename=None,
                **inputs) 
        Story.append(Spacer(1,20))

    if reportOutputFileName is not None:
        doc = SimpleDocTemplate(reportOutputFileName, pagesize=letter) 
        doc.build(Story)
        print(f"""Wrote report to file {reportOutputFileName}""")

