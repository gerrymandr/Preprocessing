import os
import numpy as np
import pandas as pd
import geopandas as gp

from tkinter import *
import tkinter
from tkinter import filedialog
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from prorationAndRoundoff import prorateWithDFs, roundoffWithDFs, getOverlayBetweenBasicAndLargeBySmall
from gen_report import prorate_report, roundoff_report
#from gen_report import prorate_report, roundoff_report
#from gen_report import prorate_and_roundoff_report, multifile_report

windowSize = [800, 450]
top = Tk()
top.geometry("x".join([str(x) for x in windowSize]))
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


num_cols=3
num_rows=4
offset = 0.03
inset_proportion=.1
# Grid Layout
rowDepth=[inset_proportion + x * (1 / (num_rows+1) + y * offset) for y in [3, 6] for x in range(num_rows)]
colDepth=[inset_proportion + x * (1 / (num_cols+1) + y * offset) for y in [0, 2] for x in range(num_cols)]
relColWidth = 1.0 / num_cols
relRowHeight = 1.0 / num_rows
thirdsSep = [4 / 72, 24 / 72, 26 / 72, 46 / 72, 48 / 72, 68 / 72]
thirdsLen = 20 / 72

clearColor = "white"
basicColor = "#AED6F1"
bigColor =   "#C9EB66"
smallColor = "#FCC06F"
lBasicColor ="#C2E0F4"
lBigColor =  "#E4F5B3"
lSmallColor ="#FDD093"
columnNamesColor = "#D3D3D3"


def selectBasicUnits():
    '''
    Allows the user to browse for a file of their basic units.
    :return: Filebath to the shapefile with their basic units.
    '''
    global basicUnits
    basicUnits = filedialog.askopenfilename()


def selectBiggerUnits():
    '''
    Allows the user to browse for a file of their bigger units.
    :return: Filebath to the shapefile with their bigger units.
    '''
    global biggerUnits
    biggerUnits = filedialog.askopenfilename()


def selectSmallestUnits():
    '''
    Allows the user to browse for a file of their smaller units.
    :return: Filebath to the shapefile with their smaller units.
    '''
    global smallestUnits
    smallestUnits = filedialog.askopenfilename()

def callback():
    '''
    Main function of the Process button to pull out the text entry fields.
    :return: Strings of all the column names specified.
    '''
    global basic_geoid, small_geoid, big_geoid, population, voting, \
        merge_basic_flag, merge_big_flag, merge_small_flag, \
        merge_basic_col, merge_biggest_col, merge_smallest_col
    basic_geoid = geoid1.get()
    big_geoid = geoid2.get()
    small_geoid = geoid3.get()
    population = popEntry.get()
    voting = voteEntry.get().split(',')
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

def selectBiggestMerge():
    '''
    Allows the user to browse for a file to merge to bigger units.
    :return: Filepath of the csv with data.
    '''
    global biggestMergePath
    biggestMergePath = filedialog.askopenfilename()

def selectSmallestMerge():
    '''
    Allows the user to browse for a file to merge to smallest units.
    :return: Filepath of the csv with data.
    '''
    global smallestMergePath
    smallestMergePath = filedialog.askopenfilename()


# 1.0: TOP ROW (title)
num1 = Frame(top)
num1.place(x=0, y=3*offset, relwidth=1, relheight=1/(num_rows))
topLabel = Label(num1, text="Preprocess that Data!", anchor=W, font="Helvetica 30")
topLabel.place(relx=thirdsSep[0], y=0, relwidth=1)

# 2.0 SELECT UNITS ROW (title)
num2 = Frame(top)
num2.place(relx=0, rely=rowDepth[0]+offset, relwidth=1, relheight=1/(num_rows))

num2_1 = Frame(num2)
num2_1.place(relx=0, rely=0, relwidth=1, relheight=0.25)
selectLabel = Label(num2_1, text="SELECT UNITS", anchor=W, font="Helvetica 14")
selectLabel.place(relx=thirdsSep[0], rely=0, relwidth=1)

# 2.1 SELECT UNITS ROW (basic)
num2_2 = Frame(num2)
num2_2.place(relx=thirdsSep[0], rely=.25, relwidth=thirdsLen, relheight=0.75)
basicf1 = Frame(num2_2, bg=basicColor)
basicf1.place(relx=0, rely=0, relwidth=1, relheight=1)
def clear_basic_idprompt(event):
    geoid1.delete(0, END)
def enable_basic_csv():
    if CheckVar1.get():
        basicMergeEntry.configure(state='normal')
        basicMerge.configure(state='normal')
    else:
        basicMergeEntry.configure(state='disabled')
        basicMerge.configure(state='disabled')
geoid1 = Entry(basicf1, width=10)
geoid1.insert(END, "Basic Units ID")
geoid1.bind("<Button-1>", clear_basic_idprompt)
geoid1.place(relx=offset, rely=0.15)
basic = Button(basicf1, text="Browse", command=selectBasicUnits, height=1, width=10)
basic.place(relx=0.5+offset, rely=0.15)
CheckVar1 = BooleanVar()
csv1 = Checkbutton(num2_2, text="add CSV data", variable=CheckVar1,
        onvalue=True, offvalue=False, height=1, width=14, bg=basicColor, command=enable_basic_csv)
csv1.pack()
csv1.place(relx=offset, rely=.65)


# 2.2 SELECT UNITS ROW (big)
num2_3 = Frame(num2)
num2_3.place(relx=thirdsSep[2], rely=.25, relwidth=thirdsLen, relheight=0.75)
bigf1 = Frame(num2_3, bg=bigColor)
bigf1.place(relx=0, rely=0, relwidth=1, relheight=1)
def clear_big_idprompt(event):
    geoid2.delete(0, END)
def enable_big_csv():
    if CheckVar2.get():
        bigMergeEntry.configure(state='normal')
        bigMerge.configure(state='normal')
    else:
        bigMergeEntry.configure(state='disabled')
        bigMerge.configure(state='disabled')
geoid2 = Entry(bigf1, width=10)
geoid2.insert(END, "Big Units ID")
geoid2.bind("<Button-1>", clear_big_idprompt)
geoid2.place(relx=offset, rely=0.15)
big = Button(bigf1, text="Browse", command=selectBiggerUnits, width=10, height=1)
big.place(relx=0.5+offset, rely=0.15)
CheckVar2 = BooleanVar()
csv2 = Checkbutton(num2_3, text="add CSV data", variable=CheckVar2,
        onvalue=True, offvalue=False, height=1, width=14, bg=bigColor, command=enable_big_csv)
csv2.pack()
csv2.place(relx=offset, rely=.65)

# 2.3 SELECT UNITS ROW (small)
num2_4 = Frame(num2)
num2_4.place(relx=thirdsSep[4], rely=.25, relwidth=thirdsLen, relheight=0.75)
smallf1 = Frame(num2_4, bg=smallColor)
smallf1.place(relx=0, rely=0, relwidth=1, relheight=1)
def clear_small_idprompt(event):
    geoid3.delete(0, END)
def enable_small_csv():
    if CheckVar3.get():
        smallMerge.configure(state='normal')
        smallMerge.configure(state='normal')
    else:
        smallMerge.configure(state='disabled')
        smallMerge.configure(state='disabled')
geoid3 = Entry(smallf1, width=10)
geoid3.insert(END, "Small Units ID")
geoid3.bind("<Button-1>", clear_small_idprompt)
geoid3.place(relx=offset, rely=0.15)
small = Button(smallf1, text="Browse", command=selectSmallestUnits, width=10, height=1)
small.place(relx=0.5+offset, rely=0.15)
CheckVar3 = BooleanVar()
csv3 = Checkbutton(num2_4, text="add CSV data", variable=CheckVar3,
        onvalue=True, offvalue=False, height=1, width=14, bg=smallColor, command=enable_small_csv)
csv3.pack()
csv3.place(relx=offset, rely=.65)

# 3.0 ADD CSV DATA (title)
num3 = Frame(top)
num3.place(relx=0, rely=rowDepth[1], relwidth=1, relheight=1/(num_rows))
num3_1 = Frame(num3)
num3_1.place(relx=0, rely=0, relwidth=1, relheight=0.2)
selectLabel = Label(num3_1, text="MERGE COLUMNS", anchor=W, font="Helvetica 14")
selectLabel.place(relx=thirdsSep[0], rely=0, relwidth=1)

# 3.1 SELECT UNITS ROW (basic)
num3_2 = Frame(num3)
num3_2.place(relx=thirdsSep[0], rely=.2, relwidth=thirdsLen, relheight=0.75)
basicf2 = Frame(num3_2, bg=lBasicColor)
basicf2.place(relx=0, rely=0, relwidth=1, relheight=1)
def clear_basic_csvidprompt(event):
    basicMergeEntry.delete(0, END)
basicMergeEntry = Entry(basicf2, width=10)
basicMergeEntry.insert(END, "Basic Units ID")
basicMergeEntry.bind("<Button-1>", clear_basic_csvidprompt)
basicMergeEntry.configure(state='disabled')
basicMergeEntry.place(relx=offset, rely=0.15)
basicMerge = Button(basicf2, text="Browse", command=selectBasicMerge, width=10, height=1)
basicMerge.configure(state='disabled')
basicMerge.place(relx=0.5+offset, rely=0.15)

# 3.2 SELECT UNITS ROW (big)
num3_3 = Frame(num3)
num3_3.place(relx=thirdsSep[2], rely=.2, relwidth=thirdsLen, relheight=0.75)
bigf2 = Frame(num3_3, bg=lBigColor)
bigf2.place(relx=0, rely=0, relwidth=1, relheight=1)
def clear_big_csvidprompt(event):
    bigMergeEntry.delete(0, END)
bigMergeEntry = Entry(bigf2, width=10)
bigMergeEntry.insert(END, "Basic Units ID")
bigMergeEntry.bind("<Button-1>", clear_big_csvidprompt)
bigMergeEntry.configure(state='disabled')
bigMergeEntry.place(relx=offset, rely=0.15)
bigMerge = Button(bigf2, text="Browse", command=selectBiggestMerge, width=10, height=1)
bigMerge.place(relx=0.5+offset, rely=0.15)

# 3.3 SELECT UNITS ROW (small)
num3_4 = Frame(num3)
num3_4.place(relx=thirdsSep[4], rely=.2, relwidth=thirdsLen, relheight=0.75)
smallf2 = Frame(num3_4, bg=lSmallColor)
smallf2.place(relx=0, rely=0, relwidth=1, relheight=1)
def clear_small_csvidprompt(event):
    smallMerge.delete(0, END)
smallMergeEntry = Entry(smallf2, width=10)
smallMergeEntry.insert(END, "Basic Units ID")
smallMergeEntry.bind("<Button-1>", clear_small_csvidprompt)
smallMergeEntry.configure(state='disabled')
smallMergeEntry.place(relx=offset, rely=0.15)
smallMerge = Button(smallf2, text="Browse", command=selectSmallestMerge, width=10, height=1)
smallMerge.place(relx=0.5+offset, rely=0.15)

# 4.0 SELECT COLUMN NAMES ROW (title)
num4 = Frame(top)
num4.place(relx=0, rely=rowDepth[2], relwidth=1, relheight=1/(num_rows))

# 4.1
num4_1 = Frame(num4, bg=columnNamesColor)
num4_1.place(relx=thirdsSep[0], rely=0, relwidth=thirdsSep[3]-thirdsSep[0], relheight=0.25)
selectLabel = Label(num4_1, text="COLUMN NAMES", anchor=W, font="Helvetica 14", bg=columnNamesColor)
selectLabel.place(relx=0, rely=0, relwidth=1)

# 4.2 
num4_2 = Frame(num4, bg=columnNamesColor)
num4_2.place(relx=thirdsSep[0], rely=.25, relwidth=thirdsSep[3]-thirdsSep[0], relheight=.75)
popCol = StringVar()
popCol.set("Population:")
popColLabel=Label(num4_2, textvariable=popCol, bg=columnNamesColor)
popColLabel.place(relx=0,rely=.25)
popEntry = Entry(num4_2, width=10)
popEntry.place(relx=.2,rely=.25)
voteCol = StringVar()
voteCol.set("Votes(comma sep):")
voteColLabel=Label(num4_2, textvariable=voteCol, bg=columnNamesColor)
voteColLabel.place(relx=.45,rely=.25)
voteEntry = Entry(num4_2, width=10)
voteEntry.place(relx=.75, rely=.25)

# 4.3
num4_3 = Frame(num4, bg=columnNamesColor)
num4_3.place(relx=thirdsSep[4], rely=0, relwidth=thirdsLen, relheight=1)
processLabel = Label(num4_3, text="ANALYSIS", anchor=W, font="Helvetica 14", bg=columnNamesColor)
processLabel.place(relx=0, rely=0, relwidth=1)

prorateVar = BooleanVar()
prorate = Checkbutton(num4_3, text="Prorate", width=10, variable=prorateVar, bg=columnNamesColor)
prorate.pack()
prorate.place(relx=0, rely=0.25)

roundoffVar = BooleanVar()
roundoff = Checkbutton(num4_3, text="Roundoff", width=10, variable=roundoffVar, bg=columnNamesColor)
roundoff.pack()
roundoff.place(relx=0, rely=.5)

reportVar = BooleanVar()
report = Checkbutton(num4_3, text="Report", width=10, variable=reportVar, bg=columnNamesColor)
report.pack()
report.place(relx=0, rely=0.75)

# Creates the button to process and pass all variables
b = Button(num4_3, text="Process", width=10, command=callback)
b.place(relx=.5, rely=.75)
top.mainloop()



basicOutputFileName="basic"

# now read files into geodataframes and join csvs if flagged
if basicUnits != '':
    basicDF = gp.read_file(basicUnits)
    if merge_basic_flag:
        basicMerge = pd.read_csv(basicMergePath)
        basicDF = bigDF.merge(basicMerge, left_on=basic_geoid, right_on=merge_basic_col)
else:
    raise Exception("ERROR: Must enter a valid file name for basic units")

if biggerUnits != '':
    bigDF = gp.read_file(biggerUnits)
    if merge_big_flag:
        bigMerge = pd.read_csv(biggestMergePath)
        bigDF = bigDF.merge(bigMerge, left_on=big_geoid, right_on=merge_biggest_col)

if len(smallestUnits)>0:
    smallDF = gp.read_file(smallestUnits)
    if merge_small_flag:
        smallMerge = pd.read_csv(smallestMergePath)
        smallDF = bigDF.merge(smallMerge, left_on=small_geoid, right_on=merge_smallest_col)
else:
    smallDF = None
lookupTable = None

reportOutputFileName=[]
p,r=False,False

if prorateVar.get():
    p=True
    lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, small_geoid, population, basic_geoid, big_geoid)
    basicOutputFileName += "Prorated"
    reportOutputFileName=["Prorated"]

    proratedValues = prorateWithDFs(bigDF, basicDF, big_geoid, basic_geoid, voting, lookupTable, 'pop')

    for i, c in enumerate(voting):
        basicDF[c] = [proratedValues[x][i] for x in basicDF[basic_geoid]]
    basicname = os.path.basename(basicUnits.split('.')[0])
    bigname = os.path.basename(biggerUnits.split('.')[0])
    prorate_report("Proration.html", [bigname, bigDF], [basicname, basicDF], smallDF, big_geoid, basic_geoid, small_geoid, population, voteColumns=voting)

if roundoffVar.get():
    r=True
    if lookupTable is None:
        lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, small_geoid, basicIDCol=basic_geoid, bigIDCol=big_geoid, bigVoteColumn=[])

    basicOutputFileName += "Rounded"
    reportOutputFileName.append("Roundoff")
    roundedValues = roundoffWithDFs(
            basicDF=basicDF, 
            bigDF=bigDF, 
            smallDF=smallDF, 
            basicID=basic_geoid, 
            bigID=big_geoid, 
            smallID=small_geoid, 
            smallPopCol=population, 
            lookup=lookupTable)
    basicDF['CD'] = [roundedValues[x] for x in basicDF[basic_geoid]]
    roundoff_report("Roundoff.html", bigDF, basicDF, big_geoid, basic_geoid)


