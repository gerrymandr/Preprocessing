import os
import random

import numpy as np
import pysal as ps
import pandas as pd
import geopandas as gp

from math import pi
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from shapely.geometry.multipolygon import MultiPolygon

roundTol=3


def write_header_styles(fstream):
    fstream.write("\n<style>\n")
    fstream.write("table { font-family: arial, sans-serif;" +
                "border-collapse: collapse; width: 100%; }\n")
    fstream.write("td, th { border: 1px solid #dddddd;" +
                "text-align: left; padding: 8px; }\n")
    fstream.write("tr:nth-child(even) { background-color: #dddddd; }\n")
    fstream.write("mycolor {#ff0000}\n")
    fstream.write("</style>\n\n")


def generic_shapefile_report(outputName, dataFrame=None, shapefileName=None,
        idColumn=None, voteColumns=None, electionDicts=None):
    """ Generate a generic report on a shapefile.
    inputs:
        :outputName:    name of file to write out report
        :dataFrame:     (optional) a geoDataFrame to do the report on.
                        If not specified, uses shapefileName
        :shapefileName: (optional) name of the shapefile to report on
        :idColumn:      (optional) unique ID column in dataFrame to look at
        :voteColumns:   (optional) list of columns of numeric data to report on
        :electionDicts: (optional) dictionary of the form:
                            - key: string(election name)
                            - val: dictionary with keys 'D' and 'R',
                                   and values: the column name in dataFrame.
                            e.g.
                            { 'presidential': {'D': 'PRES_DV08', 'R': 'PRES_RV08'}}
    """

    if dataFrame is not None:
        outputName = outputName.split('.')[0] + '.html'

        with open(outputName, "w") as f:
            picsName = f"{outputName.split('.')[0]}_images/"
            if not os.path.isdir(picsName):
                os.mkdir(picsName)

            dataFrame.plot()
            plt.savefig(picsName + "initial_plot.png")

            f.write("<html>\n")
            write_header_styles(f)

            f.write("<body>\n")
            f.write(f"<h1 width:100%> Report on {dataFrame[0]}</h1>\n")

            numUnits = len(dataFrame[1])
            numMultiUnits = sum([1 for x in dataFrame[1]["geometry"]
                if type(x) == MultiPolygon])
            neighbors = ps.weights.Rook.from_dataframe(dataFrame[1],
                    geom_col="geometry").neighbors
            numNbrs = np.array([float(len(x)) for x in neighbors.values()])
            avgNbrs = np.round(np.mean(numNbrs), roundTol)
            maxNbrs, minNbrs = max(numNbrs), min(numNbrs)

            numUnitsInsideUnits = sum([1 for x in neighbors.keys()
                                    if len(neighbors[x]) == 1])
            numIslands = sum([1 for x in neighbors.keys()
                                    if len(neighbors[x]) == 0])
            areas = np.round(np.array([float(x.area)
                for x in dataFrame[1]["geometry"]]), roundTol)
            perims = np.round(np.array([float(x.length)
                for x in dataFrame[1]["geometry"]]), roundTol)
            maxArea, minArea = max(areas), min(areas)
            avgArea = np.round(np.mean(areas), roundTol)
            maxPerim, minPerim = max(perims), min(perims)
            avgPerim = np.round(np.mean(perims), roundTol)

            polsbyPopper = np.round(4.0 * pi * areas / (perims**2), roundTol)
            avgPolsPop = np.round(np.mean(polsbyPopper), roundTol)
            maxPolsPop, minPolsPop = max(polsbyPopper), min(polsbyPopper)

            f.write(f"<h2 width:100%> Geometry: </h2>\n")
            f.write(f"<p width=100%>")
            f.write(f"<img src='{picsName}initial_plot.png' width=50%/></p>\n")
            f.write("<ul>\n")
            f.write(f"<li>{numUnits} units</li>\n")
            f.write(f"<li>{numIslands} disconnected units</li>\n")
            f.write(f"<li>{numMultiUnits} multiply connected " +
                    "or island-containing units</li>\n")
            f.write(f"<li>{numUnitsInsideUnits} units " + 
                    "completely contained inside another</li>\n")
            f.write(f"<li>Average number of neighbors: {avgNbrs}</li>\n")
            f.write(f"<li>Highest degree of connectivity: {maxNbrs}</li>\n")
            f.write(f"<li>Average, maximum, and minimum Polsby-Popper scores: ")
            f.write(f"{avgPolsPop}, {maxPolsPop}, {minPolsPop}</li>\n")
            f.write( "</ul>\n\n")

            if electionDicts is not None:
                f.write(f"<h2 width:100%> Elections Data:</h2>\n")

                for election in electionDicts.keys():
                    f.write("<p width=100%>\n")
                    electionPlot1 = picsName + election + 'D' + '.png'
                    electionPlot2 = picsName + election + 'R' + '.png'
                    c1 = electionDicts[election]
                    dataFrame[1].plot(column=c1['D'], cmap="Blues")
                    plt.savefig(electionPlot1)
                    dataFrame[1].plot(column=c1['R'], cmap="Reds")
                    plt.savefig(electionPlot2)

                    f.write(f"<h3 width=100%> {election}</h3>\n")
                    f.write(f"  <p width=100%>\nDemocrat totals: ")
                    f.write(f"{dataFrame[1][electionDicts[election]['D']].sum()}, ")
                    f.write(f"Republican Totals: ")
                    f.write(f"{dataFrame[1][electionDicts[election]['R']].sum()}\n</p>\n")
                    f.write( '  <div width=100%>\n')
                    f.write(f"    <img src='{electionPlot1}' width=45%/>\n")
                    f.write(f"    <img src='{electionPlot2}' width=45%/>\n")
                    f.write( '  </div>\n')
                    f.write( "</p>\n")

                    f.write("<br>\n")

            if voteColumns is not None:
                f.write(f"<h2 width:100%>Vote Data:</h2>\n")
                picsName = f"{outputName.split('.')[0]}_images/"
                if not os.path.isdir(picsName):
                    os.mkdir(picsName)

                f.write(f"<p>\n<table>\n<tr><th>Column Name</th><th>Total Count</th>" +
                        "<th>Max</th><th>Min</th><th>Average</th></tr>\n")
                for column in voteColumns:
                    maxCol=max(dataFrame[1][column])
                    minCol=min(dataFrame[1][column])
                    avgCol=np.mean(dataFrame[1][column].tolist())
                    f.write( "  <tr>\n")
                    f.write(f"    <td>{column}</td>\n")
                    f.write(f"    <td>{dataFrame[1][column].sum()}</td>\n")
                    f.write(f"    <td>{maxCol}</td>\n")
                    f.write(f"    <td>{minCol}</td>\n")
                    f.write(f"    <td>{avgCol}</td>\n")
                    f.write( "  </tr>\n")
                f.write("</table>\n</p>\n")
                f.write("<br>\n")
                f.write("<h3 width=100%> Vote Data Visualized</h3>\n")
                f.write("<p width=100%>\n")
                for column in voteColumns:
                    plotname = picsName + str(column) + ".png"
                    dataFrame.plot(column=column)
                    plt.title(f"{column} voting data")
                    plt.savefig(plotname)
                    f.write( "<div width=100%>\n")
                    f.write(f"  <img src='{plotname}' width=60%/>\n")
                    f.write( "</div>\n")
                f.write("</p>\n")

            f.write("</body>\n")
            f.write("</html>\n")

    elif shapefileName is not None:
        sname = os.path.basename(shapefile.split('.shp')[0])
        dataFrame = [sname, gp.read_file(shapefileName)]
        generic_shapefile_report(outputName, dataFrame, idColumn=idColumn,
                voteColumns=voteColumns, electionDicts=electionDicts)



def prorate_report(
        outputName="ProrateReport.html",
        bigDF=None,
        basicDF=None,
        smallDF=None,
        big_geoid=None,
        basic_geoid=None,
        small_geoid=None,
        population=None,
        voteColumns=None,
        electionDicts=None):

        with open(outputName, "w") as f:
            picsName = f"{outputName.split('.')[0]}_images/"
            if not os.path.isdir(picsName):
                os.mkdir(picsName)

            f.write("<html>\n")
            write_header_styles(f)

            bigAvgArea = np.round(
                    np.mean([x.area for x in bigDF[1]['geometry']]), roundTol)
            bigAvgPOP =  np.round(np.mean([x.area / (x.length**2)
                                for x in bigDF[1]['geometry']]), roundTol)
            basicAvgArea = np.round(
                    np.mean([x.area for x in basicDF[1]['geometry']]), roundTol)
            basicAvgPOP =  np.round(np.mean([x.area / (x.length**2)
                                for x in basicDF[1]['geometry']]), roundTol)
            bigDFPIC = picsName + "bigDF_init_plot.png"
            bigDF[1].plot(edgecolor='black')
            plt.savefig(bigDFPIC)
            basicDFPIC = picsName + "basicDF_init_plot.png"
            basicDF[1].plot(edgecolor='black')
            plt.savefig(basicDFPIC)

            f.write( "<body>\n")
            f.write(f"<h1 width:100%> Proration:</h1>\n")
            f.write(f"<p>{bigDF[0]} written in {basicDF[0]} Units</p>\n")
            f.write(f"\n<h2>Comparison of Shapefile geometries: </h2>\n")
            f.write( '<div width=100%>\n')
            f.write( '  <span style="width:45%;float:left">\n')
            f.write(f"    {bigDF[0]}:\n")
            f.write( "    <ul>\n")
            f.write(f"      <li> {len(bigDF[1])} units</li>\n")
            f.write(f"      <li> {bigAvgArea} average area per unit</li>\n")
            f.write(f"      <li> {bigAvgPOP} average Polsby-Popper per unit</li>\n")
            f.write( "    </ul>\n</br>\n")
            f.write(f"    <img src='{bigDFPIC}' width=100%/>\n")
            f.write( "  </span>\n")
            f.write( '  <span style="width:45%;float:right">\n')
            f.write(f"    {basicDF[0]}:\n")
            f.write( "    <ul>\n")
            f.write(f"      <li> {len(basicDF[1])} units</li>\n")
            f.write(f"      <li> {basicAvgArea} average area per unit</li>\n")
            f.write(f"      <li> {basicAvgPOP} average Polsby-Popper per unit</li>\n")
            f.write( "    </ul>\n</br>\n")
            f.write(f"    <img src='{basicDFPIC}' width=100%/>\n")
            f.write( "  </span>\n")
            f.write("</div>\n")
            f.write("</br>\n")

            if electionDicts is not None:
                f.write(f"<h2 width:100%> Elections Data:</h2>\n")
                f.write(f"<table>\n<tr><th></th>" +
                        f"<th>{bigDF[0]}</th><th>{basicDF[0]}</th></tr>\n")
                for election in electionDicts.keys():
                    f.write("<tr>\n")
                    f.write(f"<th colspan='3'> {election} </th>\n")
                    f.write("</tr>\n")
                    f.write( "<tr>")
                    f.write(f"  <td> Republican Totals </td>\n")
                    f.write( "  <td>" +
                            str(bigDF[1][electionDicts[election]['R']].sum()) +
                            "</td>\n")
                    f.write( "  <td>" +
                            str(basicDF[1][electionDicts[election]['R']].sum()) +
                            "</td>\n")
                    f.write( "</tr>\n")
                    f.write( "<tr>\n")
                    f.write(f"<td> Democrat Totals </td>")
                    f.write("<td>" +
                            str(bigDF[1][electionDicts[election]['D']].sum()) +
                            "</td>\n")
                    f.write("<td>" +
                            str(basicDF[1][electionDicts[election]['D']].sum()) +
                            "</td>\n")
                    f.write("</tr>\n")
                f.write("</table>\n")

                for election in electionDicts.keys():
                    electionPlot1 =  picsName + election + 'D' + '.png'
                    electionPlot2 =  picsName + election + 'R' + '.png'
                    delectionPlot1 = picsName + 'orig_' + election + 'D' + '.png'
                    delectionPlot2 = picsName + 'orig_' + election + 'R' + '.png'

                    basicDF[1].plot(column=electionDicts[election]['D'], cmap='Blues')
                    plt.title(f"prorated to {basicDF[0]}")
                    plt.savefig(electionPlot1)
                    plt.clf()
                    bigDF[1].plot(column=electionDicts[election]['D'], cmap='Blues')
                    plt.title(f"original data source: {bigDF[0]}")
                    plt.savefig(delectionPlot1)
                    plt.clf()
                    basicDF[1].plot(column=electionDicts[election]['R'], cmap='Reds')
                    plt.title(f"prorated to {basicDF[0]}")
                    plt.savefig(electionPlot2)
                    plt.clf()
                    bigDF[1].plot(column=electionDicts[election]['R'], cmap='Reds')
                    plt.title(f"original data source: {bigDF[0]}")
                    plt.savefig(delectionPlot2)
                    plt.clf()

                    f.write(f"<h1 width:100%>{election} Election:</h1>\n")
                    f.write('<div width=100%>\n')
                    f.write(f"   <img src='{delectionPlot1}' width=45%/>\n")
                    f.write(f"   <img src='{electionPlot1}'  width=45%/>\n")
                    f.write( '</div>\n')
                    f.write('<div width=100%>\n')
                    f.write(f"   <img src='{delectionPlot2}' width=45%/>\n")
                    f.write(f"   <img src='{electionPlot2}'  width=45%/>\n")
                    f.write('</div>\n')
                f.write("</br>\n")

            if voteColumns is not None:
                f.write(f"<h2 width=100%> Voting Data:</h2>\n")

                picsName = f"{outputName.split('.')[0]}_images/"
                if not os.path.isdir(picsName):
                    os.mkdir(picsName)

                f.write(f"<h3 width=100%> Original counts</h3>\n")
                f.write(f"<p>\n<table>\n<tr><th>Column Name</th><th>Total Count" +
                        "</th><th>Max</th><th>Min</th><th>Average</th></tr>\n")
                for column in voteColumns:
                    maxCol = np.round(max(bigDF[1][column]), roundTol)
                    minCol = np.round(min(bigDF[1][column]), roundTol)
                    avgCol = np.round(np.mean(basicDF[1][column].tolist()), roundTol)
                    f.write("<tr>\n")
                    f.write(f"<td>{column}</td>\n")
                    f.write(f"<td>{bigDF[1][column].sum()}</td>\n")
                    f.write(f"<td>{maxCol}</td>\n")
                    f.write(f"<td>{minCol}</td>\n")
                    f.write(f"<td>{avgCol}</td>\n")
                    f.write("</tr>\n")
                f.write("</table>\n</p>\n")

                f.write(f"<h3 width=100%> Prorated counts</h3>\n")
                f.write(f"<p>\n<table>\n<tr><th>Column Name</th><th>Total Count</th>" +
                        "<th>Max</th><th>Min</th><th>Average</th></tr>\n")
                for column in voteColumns:
                    maxCol = np.round(max(basicDF[1][column]), roundTol)
                    minCol = np.round(min(basicDF[1][column]), roundTol)
                    avgCol = np.round(np.mean(basicDF[1][column].tolist()), roundTol)
                    f.write("<tr>\n")
                    f.write(f"<td>{column}</td>\n")
                    f.write(f"<td>{basicDF[1][column].sum()}</td>\n")
                    f.write(f"<td>{maxCol}</td>\n")
                    f.write(f"<td>{minCol}</td>\n")
                    f.write(f"<td>{avgCol}</td>\n")
                    f.write("</tr>\n")
                f.write("</table>\n</p>\n")
                f.write("<br>\n")

                f.write("<h3 width=100%> Vote Data Visualized</h3>\n")
                f.write("<p width=100%>\n")
                for column in voteColumns:
                    # original
                    oplotname = picsName + str(column) + "_o.png"
                    bigDF[1].plot(column=column)
                    plt.title(f" Original {column} voting data")
                    plt.savefig(oplotname)
                    # prorated
                    pplotname = picsName + str(column) + "_p.png"
                    basicDF[1].plot(column=column)
                    plt.title(f" Prorated {column} voting data")
                    plt.savefig(pplotname)
                    f.write(f"<div width=100%>\n")
                    f.write(f"    <img src='{oplotname}' width=45%/>\n")
                    f.write(f"    <img src='{pplotname}' width=45%/>\n")
                    f.write(f"</div>\n")
                f.write("</p>\n")

            f.write("</body>\n")
            f.write("</html>\n")


def roundoff_report(
        outputName="RoundoffReport.html",
        bigDF=None,
        basicDF=None,
        big_geoid=None,
        basic_geoid=None,
        lookupTable=None):

        with open(outputName, "w") as f:

            picsName = f"{outputName.split('.')[0]}_images/"
            if not os.path.isdir(picsName):
                os.mkdir(picsName)

            bigUnits = picsName+"bigV.png"
            basicUnits = picsName+"basicV.png"
            roundedUnits = picsName+"roundedV.png"

            bigDF.plot(column=big_geoid, cmap='YlGnBu')
            plt.title("Before Rounding")
            plt.savefig(bigUnits)

            # randomize the colors so that vtds show up
            l1 = [x for x in basicDF[basic_geoid]]
            random.shuffle(l1)
            basicDF['random'] = l1
            basicDF.plot(column='random', cmap='Blues')
            plt.title("Roundoff Units")
            plt.savefig(basicUnits)

            basicDF.plot(column='CD', cmap='YlGnBu')
            plt.title("After Rounding")
            plt.savefig(roundedUnits)

            f.write("<html>\n")
            write_header_styles(f)
            f.write("<body>\n")

            f.write(f"<h2 width=100%> Roundoff Results</h2>\n")
            f.write( "<p>\n")
            f.write( '  <div width=100%>\n')
            f.write(f"    <img src='{bigUnits}' width=30%/>\n")
            f.write(f"    <img src='{basicUnits}' width=30%/>\n")
            f.write(f"    <img src='{roundedUnits}' width=30%/>\n")
            f.write( '  </div>\n')
            f.write( '  <div width=100%>\n')
            f.write(f"    <span width=33%>\n")
            f.write(f"       {len(bigDF)} Units\n")
            f.write(f"    </span>" )
            f.write(f"    <span width=33%>\n")
            f.write(f"       {len(basicDF)} Units\n")
            f.write(f"    </span>" )
            f.write(f"    <span width=33%>\n")
            f.write(f"      {len(basicDF)} units with attribute 'CD'\n")
            f.write(f"    </span>" )
            '''
            '''
            f.write( '  </div>\n')
            f.write( "</p>\n")

            if lookupTable is not None:
                f.write("<h2 width=100%>How closely did the maps align?</h2>\n")
                orig_num_basic = len(basicDF)
                split_num_basic = len(lookupTable['basicUnits'])

                f.write(f"<p>During roundoff, {split_num_basic - orig_num_basic}")
                f.write(" boundaries had to be resolved.</p>\n")

                # get all of the units in basicDF that have multiple bigDF entries
                # that correspond to it(i.e. the ones that are split by bigDF units)
                basicsplit = [x for x in lookupTable["basicUnits"].unique()
                        if len(lookupTable.loc[lookupTable["basicUnits"]== x, :]) > 1]

                # get the average number of pieces each of the split basicUnits is in
                splitOnes = lookupTable.loc[
                        lookupTable['basicUnits'].isin(basicsplit),
                        ["area", "basicUnits"]]
                avgNumOfSplits = len(splitOnes) * 1.0 / len(basicsplit)

                # get area of each piece
                basicsplit = splitOnes["basicUnits"].tolist()
                intersectArea = np.array(splitOnes['area'].tolist())

                basicsplitsize = [basicDF.loc[basicDF[basic_geoid] == x, "geometry"]
                        for x in basicsplit]
                areas = [float(x.area) for x in basicsplitsize]
                basicsplitproportion = intersectArea / areas
                basicsplitproportion = [x for i, x in enumerate(basicsplitproportion)
                        if i < len(basicsplitproportion/2)]
                nbasicsplit = len(set(basicsplit))

                f.write( "<p>\n  <ul>\n")
                f.write(f"  <li> Average number of pieces per split unit: " +
                        f"{avgNumOfSplits}</li>\n")
                f.write(f"  <li> Average area of split per unit: " +
                        f"{np.mean(intersectArea)}</li>\n")
                f.write(f"   <li> Smallest split was " +
                        f"{np.round(min(basicsplitproportion), roundTol)} " +
                        "fraction of original area</li>\n")
                f.write(f"   <li> Average split proportion: " +
                        f"{np.mean(basicsplitproportion)} " +
                        "percent of original area</li>\n")
                f.write("</ul>\n</p>\n")

                CD = dict([(y, x) for x, y in enumerate(basicDF['CD'].unique())])
                N = 10 * len(CD)
                basicDF['wasSplit'] = [N if x in basicsplit else
                        CD[basicDF.loc[basicDF[basic_geoid] == x, 'CD'].tolist()[0]]
                        for x in basicDF[basic_geoid].tolist()]

                basicDF.plot(column='wasSplit')
                plt.savefig(picsName+"SPLIT.png")
                f.write("<div width=100%>\n")
                f.write("<h3>Rounded Units with Splits Highlighted:</h3>\n")
                f.write(f"<img src={picsName+'SPLIT.png'} />\n</div>\n")

            f.write("</body>\n")
            f.write("</html>\n")
