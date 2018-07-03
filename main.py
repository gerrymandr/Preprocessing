import os
import numpy as np
import pandas as pd
import geopandas as gp

from tkinter import *
import tkinter
from tkinter import filedialog

from prorationAndRoundoff import prorateWithDFs, roundoffWithDFs, getLookupTable, getOverlayBetweenBasicAndLargeBySmall
from gen_report import prorate_and_roundoff_report, multifile_report

windowSize = [615, 325]
top = Tk()
top.geometry("615x325")
#top.resizable(False, False)
top.title('Preprocess that data!')

basicUnits = ''
biggerUnits = ''
smallestUnits = ''
basic_geoid = ''
big_geoid = ''
small_geoid = ''
population = ''
voting = ''
cond_dist = ''
merge_basic_flag = False
merge_big_flag = False
merge_small_flag = False
basicMergePath = ''
biggestMergePath = ''
smallestMergePath = ''
merge_basic_col = ''
merge_biggest_col = ''
merge_smallest_col = ''


image = tkinter.PhotoImage(file="check1.png")
check1 = tkinter.Label(image=image)
check2 = tkinter.Label(image=image)
check3 = tkinter.Label(image=image)
check4 = tkinter.Label(image=image)
check5 = tkinter.Label(image=image)
check6 = tkinter.Label(image=image)

def selectBasicUnits():
    '''
    Allows the user to browse for a file of their basic units.
    :return: Filebath to the shapefile with their basic units.
    '''
    global basicUnits
    basicUnits = filedialog.askopenfilename()
    if basicUnits:
        #check1.place(x=85, y=55)
        check1.place(relx=85./windowSize[0], rely=55./windowSize[1])

def selectBiggerUnits():
    '''
    Allows the user to browse for a file of their bigger units.
    :return: Filebath to the shapefile with their bigger units.
    '''
    global biggerUnits
    biggerUnits = filedialog.askopenfilename()
    if biggerUnits:
        #check2.place(x=285, y=55)
        check2.place(relx=285./windowSize[0], rely=55./windowSize[1])

def selectSmallestUnits():
    '''
    Allows the user to browse for a file of their smaller units.
    :return: Filebath to the shapefile with their smaller units.
    '''
    global smallestUnits
    smallestUnits = filedialog.askopenfilename()
    if smallestUnits:
        #check3.place(x=485, y=55)
        check3.place(relx=485./windowSize[0], rely=55./windowSize[1])

def callback():
    '''
    Main function of the Process button to pull out the text entry fields.
    :return: Strings of all the column names specified.
    '''
    global basic_geoid, small_geoid, big_geoid, population, voting, cong_dist, \
        merge_basic_flag, merge_big_flag, merge_small_flag, \
        merge_basic_col, merge_biggest_col, merge_smallest_col
    basic_geoid = geoid1.get()
    big_geoid = geoid2.get()
    small_geoid = geoid3.get()
    population = popEntry.get()
    voting = voteEntry.get().split(',')
    cong_dist = cdEntry.get()
    merge_basic_flag = CheckVar1.get()
    merge_big_flag = CheckVar2.get()
    merge_small_flag = CheckVar3.get()
    merge_basic_col = basicMergeEntry.get()
    merge_biggest_col = bigMergeEntry.get()
    merge_smallest_col = smallMergeEntry.get()
    top.destroy()

def selectBasicMerge():
    '''
    Allows the user to browse for a file to merge to basic units.
    :return: Filepath of the csv with data.
    '''
    global basicMergePath
    basicMergePath = filedialog.askopenfilename()
    if basicUnits:
        check4.place(relx=285./windowSize[0], rely=155./windowSize[1])

def selectBiggestMerge():
    '''
    Allows the user to browse for a file to merge to bigger units.
    :return: Filepath of the csv with data.
    '''
    global biggestMergePath
    biggestMergePath = filedialog.askopenfilename()
    if basicUnits:
        check5.place(relx=285./windowSize[0], rely=205./windowSize[1])

def selectSmallestMerge():
    '''
    Allows the user to browse for a file to merge to smallest units.
    :return: Filepath of the csv with data.
    '''
    global smallestMergePath
    smallestMergePath = filedialog.askopenfilename()
    if basicUnits:
        check6.place(relx=285./windowSize[0], rely=255./windowSize[1])

# Creates the ability to load your basic units
# and specify your identifier column
var1 = StringVar()
label1 = Label(top, textvariable=var1)
var1.set("Select your basic units")
label1.pack()
label1.place(relx=25./windowSize[0], rely=25./windowSize[1])
geoid1 = Entry(top, width=10)
geoid1.pack()
geoid1.place(relx=115./windowSize[0], rely=55./windowSize[1])

# Creates the checkbox to signal if you are pulling
# in other data (basic units)
CheckVar1 = BooleanVar()
csv1 = Checkbutton(top, text="add CSV data", variable=CheckVar1, onvalue=True, offvalue=False, height=1, width=14)
csv1.pack()
csv1.place(relx=25./windowSize[0], rely=80./windowSize[1])

# Creates the browse button to load the file (basic units)
basic = Button(top, text="Browse", command=selectBasicUnits)
basic.place(relx=25./windowSize[0], rely=50./windowSize[1])

# Creates the ability to load your bigger units
# and specify your identifier column
var2 = StringVar()
label2 = Label(top, textvariable=var2)
var2.set("Select your bigger units")
label2.pack()
label2.place(relx=225./windowSize[0], rely=25./windowSize[1])
geoid2 = Entry(top, width=10)
geoid2.pack()
geoid2.place(relx=315./windowSize[0],rely=55./windowSize[1])

# Creates the checkbox to signal if you are pulling
# in other data (bigger units)
CheckVar2 = BooleanVar()
csv2 = Checkbutton(top, text="add CSV data", variable=CheckVar2, onvalue=True, offvalue=False, height=1, width=14)
csv2.pack()
csv2.place(relx=225./windowSize[0], rely=80./windowSize[1])

# Creates the browse button to load the file (bigger units)
bigger = Button(top, text="Browse", command=selectBiggerUnits)
bigger.place(relx=225./windowSize[0], rely=50./windowSize[1])

# Creates the ability to load your smallest units
# and specify your identifier column
var3 = StringVar()
label3 = Label(top, textvariable=var3)
var3.set("Select your smallest units")
label3.pack()
label3.place(relx=425./windowSize[0], rely=25./windowSize[1])
geoid3 = Entry(top, width=10)
geoid3.pack()
geoid3.place(relx=515./windowSize[0],rely=55./windowSize[1])

# Creates the checkbox to signal if you are pulling
# in other data (smallest units)
CheckVar3 = BooleanVar()
csv3 = Checkbutton(top, text="add CSV data", variable=CheckVar3, onvalue=True, offvalue=False, height=1, width=14)
csv3.pack()
csv3.place(relx=425./windowSize[0], rely=80./windowSize[1])

# Creates the browse button to load the file (smallest units)
smallest = Button(top, text="Browse", command=selectSmallestUnits)
smallest.place(relx=425./windowSize[0], rely=50./windowSize[1])

# Creates the entry fields for your population column
popCol = StringVar()
popColLabel = Label(top, textvariable=popCol)
popCol.set("Enter your population column")
popColLabel.pack()
popColLabel.place(relx=25./windowSize[0], rely=125./windowSize[1])
popEntry = Entry(top, width=10)
popEntry.pack()
popEntry.place(relx=25./windowSize[0],rely=150./windowSize[1])

# Creates the entry fields for your vote column
voteCol = StringVar()
voteColLabel = Label(top, textvariable=voteCol)
voteCol.set("Enter your vote column")
voteColLabel.pack()
voteColLabel.place(relx=25./windowSize[0], rely=175./windowSize[1])
voteEntry = Entry(top, width=10)
voteEntry.pack()
voteEntry.place(relx=25./windowSize[0],rely=200./windowSize[1])

# Creates the entry fields for your CD column
cdCol = StringVar()
cdColLabel = Label(top, textvariable=cdCol)
cdCol.set("Enter your CD column")
cdColLabel.pack()
cdColLabel.place(relx=25./windowSize[0], rely=225./windowSize[1])
cdEntry = Entry(top, width=10)
cdEntry.pack()
cdEntry.place(relx=25./windowSize[0],rely=250./windowSize[1])

# Creates entry field to list column you want for
# merging in csv data (basic units)
basicMergeCol = StringVar()
basicMergeLabel = Label(top, textvariable=basicMergeCol)
basicMergeCol.set("Basic Units Merge Column")
basicMergeLabel.pack()
basicMergeLabel.place(relx=225./windowSize[0], rely=125./windowSize[1])
basicMergeEntry = Entry(top, width=10)
basicMergeEntry.pack()
basicMergeEntry.place(relx=315./windowSize[0],rely=155./windowSize[1])

# Creates entry field to list column you want for
# merging in csv data (biggest units)
bigMergeCol = StringVar()
bigMergeLabel = Label(top, textvariable=bigMergeCol)
bigMergeCol.set("Bigger Units Merge Column")
bigMergeLabel.pack()
bigMergeLabel.place(relx=225./windowSize[0], rely=175./windowSize[1])
bigMergeEntry = Entry(top, width=10)
bigMergeEntry.pack()
bigMergeEntry.place(relx=315./windowSize[0],rely=205./windowSize[1])

# Creates entry field to list column you want for
# merging in csv data (smallest units)
smallMergeCol = StringVar()
smallMergeLabel = Label(top, textvariable=smallMergeCol)
smallMergeCol.set("Smallest Units Merge Column")
smallMergeLabel.pack()
smallMergeLabel.place(relx=225./windowSize[0], rely=225./windowSize[1])
smallMergeEntry = Entry(top, width=10)
smallMergeEntry.pack()
smallMergeEntry.place(relx=315./windowSize[0],rely=255./windowSize[1])

# Creates the browse option (basic units)
basicMerge = Button(top, text="Browse", command=selectBasicMerge)
basicMerge.place(relx=225./windowSize[0], rely=150./windowSize[1])

# Creates the browse option (bigger units)
biggestMerge = Button(top, text="Browse", command=selectBiggestMerge)
biggestMerge.place(relx=225./windowSize[0], rely=200./windowSize[1])

# Creates the browse option (smallest units)
smallestMerge = Button(top, text="Browse", command=selectSmallestMerge)
smallestMerge.place(relx=225./windowSize[0], rely=250./windowSize[1])

prorateVar = BooleanVar()
prorate = Checkbutton(top, text="Prorate", width=10, variable=prorateVar)
prorate.pack()
prorate.place(relx=500./windowSize[0], rely=125./windowSize[1])

roundoffVar = BooleanVar()
roundoff = Checkbutton(top, text="Roundoff", width=10, variable=roundoffVar)
roundoff.pack()
roundoff.place(relx=500./windowSize[0], rely=162./windowSize[1])

reportVar = BooleanVar()
report = Checkbutton(top, text="Report", width=10, variable=reportVar)
report.pack()
report.place(relx=500./windowSize[0], rely=200./windowSize[1])

# Creates the button to process and pass all variables
b = Button(top, text="Process", width=10, command=callback)
b.pack()
b.place(relx=500./windowSize[0], rely=250./windowSize[1])

top.mainloop()

basicOutputFileName="basic"

# now read files into geodataframes
if biggerUnits != '':
    bigDF = gp.read_file(biggerUnits)
if basicUnits != '':
    basicDF = gp.read_file(basicUnits)
if len(smallestUnits)>0:
    smallDF = gp.read_file(smallestUnits)
else:
    smallDF = None
lookupTable = None

reportOutputFileName=[]

if prorateVar.get():
    lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, small_geoid, basic_geoid, big_geoid, voting)
    basicOutputFileName += "Prorated"
    reportOutputFileName=["Prorated"]
    proratedValues = prorateWithDFs(bigDF, basicDF, smallDF, big_geoid, basic_geoid, small_geoid, population, voting, lookupTable)

    for i, c in enumerate(voting):
        basicDF[c] = [proratedValues[x][i] for x in basicDF[basic_geoid]]

if roundoffVar.get():
    if lookupTable is None:
        lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, small_geoid, basic_geoid, big_geoid, voting)
    basicOutputFileName += "Rounded"
    reportOutputFileName.append("Roundoff")
    roundedValues = roundoffWithDFs(basicDF, bigDF, smallDF, basic_geoid, big_geoid, small_geoid, population, lookupTable)
    basicDF['CD'] = [roundedValues[x] for x in basicDF[basic_geoid]]


basicDF.to_file(basicOutputFileName+".shp")
print("wrote to new shapefile: %s"%basicOutputFileName)

# output data for report generation
if reportVar.get():
    if len(reportOutputFileName) < 1:
        names = [x for x in [biggerUnits, basicUnits, smallestUnits] if x != '']
        cleaned_names = [os.path.basename(x).split(".")[0] for x in names]

        reportOutputFileName = "_and_".join(cleaned_names)+"_report.pdf"
        input_list = []
        if biggerUnits != '':
            input_list.append([biggerUnits, big_geoid])
        if basicUnits != '':
            input_list.append([basicUnits, basic_geoid])
        if smallestUnits != '':
            input_list.append([smallestUnits, small_geoid])
        multifile_report(reportOutputFileName, input_list)
    
    else:
        reportOutputFileName = "_and_".join(reportOutputFileName)+"_report.pdf"
        prorate_and_roundoff_report(reportOutputFileName, biggerUnits, basicUnits, smallestUnits, big_geoid, basic_geoid, small_geoid, population, voting, lookupTable)
