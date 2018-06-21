from tkinter import *
import tkinter
from tkinter import filedialog

top = Tk()
top.geometry("700x600")

basicUnits = ''
biggerUnits = ''
smallestUnits = ''
basic_geoid = ''
big_geoid = ''
small_geoid = ''
population = ''
voting = ''
cond_dist = ''
merge_basic = False
merge_big = False
merge_small = False
basicMergePath = ''
biggestMergePath = ''
smallestMergePath = ''

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
        check1.place(x=85, y=55)

def selectBiggerUnits():
    '''
    Allows the user to browse for a file of their bigger units.
    :return: Filebath to the shapefile with their bigger units.
    '''
    global biggerUnits
    biggerUnits = filedialog.askopenfilename()
    if biggerUnits:
        check2.place(x=285, y=55)

def selectSmallestUnits():
    '''
    Allows the user to browse for a file of their smaller units.
    :return: Filebath to the shapefile with their smaller units.
    '''
    global smallestUnits
    smallestUnits = filedialog.askopenfilename()
    if smallestUnits:
        check3.place(x=485, y=55)

def callback():
    '''
    Main function of the Process button to pull out the text entry fields.
    :return: Strings of all the column names specified.
    '''
    global basic_geoid, small_geoid, big_geoid, population, voting, cong_dist, merge_basic, merge_big, merge_small
    basic_geoid = geoid1.get()
    big_geoid = geoid2.get()
    small_geoid = geoid3.get()
    population = popEntry.get()
    voting = voteEntry.get()
    cong_dist = cdEntry.get()
    merge_basic = CheckVar1.get()
    merge_big = CheckVar2.get()
    merge_small = CheckVar3.get()
    top.destroy()

def selectBasicMerge():
    '''
    Allows the user to browse for a file to merge to basic units.
    :return: Filepath of the csv with data.
    '''
    global basicMergePath
    basicMergePath = filedialog.askopenfilename()
    if basicUnits:
        check4.place(x=285, y=155)

def selectBiggestMerge():
    '''
    Allows the user to browse for a file to merge to bigger units.
    :return: Filepath of the csv with data.
    '''
    global biggestMergePath
    biggestMergePath = filedialog.askopenfilename()
    if basicUnits:
        check5.place(x=285, y=205)

def selectSmallestMerge():
    '''
    Allows the user to browse for a file to merge to smallest units.
    :return: Filepath of the csv with data.
    '''
    global smallestMergePath
    smallestMergePath = filedialog.askopenfilename()
    if basicUnits:
        check6.place(x=285, y=255)

# Creates the ability to load your basic units
# and specify your identifier column
var1 = StringVar()
label1 = Label(top, textvariable=var1)
var1.set("Select your basic units")
label1.pack()
label1.place(x=25, y=25)
geoid1 = Entry(top, width=10)
geoid1.pack()
geoid1.place(x=115, y=55)

# Creates the checkbox to signal if you are pulling
# in other data (basic units)
CheckVar1 = BooleanVar()
csv1 = Checkbutton(top, text="CSV (data to merge)", variable=CheckVar1, onvalue=True, offvalue=False, height=1, width=14)
csv1.pack()
csv1.place(x=25, y=80)

# Creates the browse button to load the file (basic units)
basic = Button(top, text="Browse", command=selectBasicUnits)
basic.place(x=25, y=50)

# Creates the ability to load your bigger units
# and specify your identifier column
var2 = StringVar()
label2 = Label(top, textvariable=var2)
var2.set("Select your bigger units")
label2.pack()
label2.place(x=225, y=25)
geoid2 = Entry(top, width=10)
geoid2.pack()
geoid2.place(x=315,y=55)

# Creates the checkbox to signal if you are pulling
# in other data (bigger units)
CheckVar2 = BooleanVar()
csv2 = Checkbutton(top, text="CSV (data to merge)", variable=CheckVar2, onvalue=True, offvalue=False, height=1, width=14)
csv2.pack()
csv2.place(x=225, y=80)

# Creates the browse button to load the file (bigger units)
bigger = Button(top, text="Browse", command=selectBiggerUnits)
bigger.place(x=225, y=50)

# Creates the ability to load your smallest units
# and specify your identifier column
var3 = StringVar()
label3 = Label(top, textvariable=var3)
var3.set("Select your smallest units")
label3.pack()
label3.place(x=425, y=25)
geoid3 = Entry(top, width=10)
geoid3.pack()
geoid3.place(x=515,y=55)

# Creates the checkbox to signal if you are pulling
# in other data (smallest units)
CheckVar3 = BooleanVar()
csv3 = Checkbutton(top, text="CSV (data to merge)", variable=CheckVar3, onvalue=True, offvalue=False, height=1, width=14)
csv3.pack()
csv3.place(x=425, y=80)

# Creates the browse button to load the file (smallest units)
smallest = Button(top, text="Browse", command=selectSmallestUnits)
smallest.place(x=425, y=50)

# Creates the entry fields for your population column
popCol = StringVar()
popColLabel = Label(top, textvariable=popCol)
popCol.set("Enter your population column")
popColLabel.pack()
popColLabel.place(x=25, y=125)
popEntry = Entry(top, width=10)
popEntry.pack()
popEntry.place(x=25,y=150)

# Creates the entry fields for your vote column
voteCol = StringVar()
voteColLabel = Label(top, textvariable=voteCol)
voteCol.set("Enter your vote column")
voteColLabel.pack()
voteColLabel.place(x=25, y=175)
voteEntry = Entry(top, width=10)
voteEntry.pack()
voteEntry.place(x=25,y=200)

# Creates the entry fields for your CD column
cdCol = StringVar()
cdColLabel = Label(top, textvariable=cdCol)
cdCol.set("Enter your CD column")
cdColLabel.pack()
cdColLabel.place(x=25, y=225)
cdEntry = Entry(top, width=10)
cdEntry.pack()
cdEntry.place(x=25,y=250)

# Creates entry field to list column you want for
# merging in csv data (basic units)
basicMergeCol = StringVar()
basicMergeLabel = Label(top, textvariable=basicMergeCol)
basicMergeCol.set("Basic Units Merge Column")
basicMergeLabel.pack()
basicMergeLabel.place(x=225, y=125)
basicMergeEntry = Entry(top, width=10)
basicMergeEntry.pack()
basicMergeEntry.place(x=315,y=155)

# Creates entry field to list column you want for
# merging in csv data (biggest units)
bigMergeCol = StringVar()
bigMergeLabel = Label(top, textvariable=bigMergeCol)
bigMergeCol.set("Bigger Units Merge Column")
bigMergeLabel.pack()
bigMergeLabel.place(x=225, y=175)
bigMergeEntry = Entry(top, width=10)
bigMergeEntry.pack()
bigMergeEntry.place(x=315,y=205)

# Creates entry field to list column you want for
# merging in csv data (smallest units)
smallMergeCol = StringVar()
smallMergeLabel = Label(top, textvariable=smallMergeCol)
smallMergeCol.set("Smallest Units Merge Column")
smallMergeLabel.pack()
smallMergeLabel.place(x=225, y=225)
smallMergeEntry = Entry(top, width=10)
smallMergeEntry.pack()
smallMergeEntry.place(x=315,y=255)

# Creates the browse option (basic units)
basicMerge = Button(top, text="Browse", command=selectBasicMerge)
basicMerge.place(x=225, y=150)

# Creates the browse option (bigger units)
biggestMerge = Button(top, text="Browse", command=selectBiggestMerge)
biggestMerge.place(x=225, y=200)

# Creates the browse option (smallest units)
smallestMerge = Button(top, text="Browse", command=selectSmallestMerge)
smallestMerge.place(x=225, y=250)

# Creates the button to process and pass all variables
b = Button(top, text="Process", width=10, command=callback)
b.pack()
b.place(x=600, y=500)

top.mainloop()

# All variables that get passed
print(basicUnits)
print(biggerUnits)
print(smallestUnits)
print(basic_geoid)
print(big_geoid)
print(small_geoid)
print(population)
print(voting)
print(cong_dist)
print(merge_basic)
print(merge_big)
print(merge_small)
print(basicMergePath)
print(biggestMergePath)
print(smallestMergePath)
