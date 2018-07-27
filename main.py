import os
import numpy as np
import pandas as pd
import geopandas as gp
import tkinter as tk

from functools import partial

from tkinter import ttk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

from prorationAndRoundoff import (prorateWithDFs,
        roundoffWithDFs,
        getOverlayBetweenBasicAndLargeBySmall)

from gen_report import (prorate_report,
        roundoff_report,
        generic_shapefile_report)

windowSize = [800, 425]

num_cols=3
num_rows=3
offset = .01
inset_proportion=.1
# Grid Layout
rowDepth = [.2, .5, .6, .9, .99]

thirdsSep = [2 / 72,
            24 / 72,
            25 / 72, 
            47 / 72, 
            48 / 72, 
            70 / 72]

thirdsLen = 22 / 72

clearColor = "white"
basicColor = "#AED6F1"
bigColor =   "#C9EB66"
smallColor = "#FCC06F"
lBasicColor ="#C2E0F4"
lBigColor =  "#E4F5B3"
lSmallColor ="#FDD093"
columnNamesColor = "#D3D3D3"


def callback(page):
    '''
    Main function of the Process button to pull out the text entry fields.
    :return: Strings of all the column names specified.
    '''

    basic_geoid = page.geoid1.get()
    big_geoid = page.geoid2.get()
    small_geoid = page.geoid3.get()
    population = page.popEntry.get()
    voting = page.voteEntry.get().split(',')
    merge_basic_col = page.basicMergeEntry.get()
    merge_biggest_col = page.bigMergeEntry.get()
    merge_smallest_col = page.smallMergeEntry.get()
    
    # now read files into geodataframes and join csvs if flagged
    if page.basicUnits != '':
        basicDF = gp.read_file(page.basicUnits)
        if merge_basic_col != '' and page.basicMergePath != '':
            filename = page.basicMergePath
            if filename.split(".")[-1] == "csv":
                basicMerge = pd.read_csv(page.basicMergePath)
            elif filename.split(".")[-1] == "xlsx":
                basicMerge = pd.read_excel(page.basicMergePath)
            basicDF = basicDF.merge(basicMerge,
                    left_on=basic_geoid, right_on=merge_basic_col)
        basicDF.fillna("0", inplace=True)
    else:
        raise Exception("ERROR: Must enter a valid file name for basic units")

    if page.biggerUnits != '':
        bigDF = gp.read_file(page.biggerUnits)
        if merge_biggest_col != '' and page.biggestMergePath != '':
            filename = page.biggestMergePath
            if filename.split(".")[-1] == "csv":
                bigMerge = pd.read_csv(page.biggestMergePath)
            elif filename.split(".")[-1] == "xlsx":
                bigMerge = pd.read_excel(page.biggestMergePath)
            bigDF = bigDF.merge(bigMerge,
                    left_on=big_geoid, right_on=merge_biggest_col)
        bigDF.fillna("0", inplace=True)

    if len(page.smallestUnits)>0:
        smallDF = gp.read_file(page.smallestUnits)
        if merge_smallest_col != '' and page.smallestMergePath != '':
            filename = page.basicMergePath
            if filename.split(".")[-1] == "csv":
                smallMerge = pd.read_csv(page.smallestMergePath)
            elif filename.split(".")[-1] == "xlsx":
                smallMerge = pd.read_excel(page.smallMergePath)
            smallDF = bigDF.merge(smallMerge,
                    left_on=small_geoid, right_on=merge_smallest_col)
        smallDF.fillna("0", inplace=True)
    else:
        smallDF = None
    lookupTable = None

    if page.title == 'Prorate':
        lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF,
                small_geoid, population, basic_geoid, big_geoid)
        proratedValues = prorateWithDFs(bigDF, basicDF, big_geoid, basic_geoid,
                voting, lookupTable, prorateCol='pop')

        mylist = set(basicDF[basic_geoid]) - set(proratedValues.keys())
        if len(mylist) > 0:
            print("WARNING: the following vtds were not allocated any votes: ")
            print(mylist)
            print("Check your CRS of each shapefile to see if the maps are aligned")

        for i, c in enumerate(voting):
            basicDF[c] = [proratedValues[x][i] if x not in mylist else 0
                    for x in basicDF[basic_geoid]]

        basicDF.to_file("Prorated.shp")
        print("\nwrote to new shapefile: Prorated.shp\n")

        basicname = os.path.basename(page.basicUnits.split('.')[0])
        bigname = os.path.basename(page.biggerUnits.split('.')[0])
        prorate_report("Proration.html",
                [bigname, bigDF], [basicname, basicDF],
                smallDF, big_geoid, basic_geoid, small_geoid,
                population, voteColumns=voting)
        print("\nReport written to file: Proration.html\n")
        page.destroyall()

    elif page.title == 'Roundoff':
        if lookupTable is None:
            lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF,
                    small_geoid, population, basic_geoid, big_geoid)
        roundedValues = roundoffWithDFs( basicDF=basicDF, bigDF=bigDF, smallDF=smallDF, 
            basicID=basic_geoid, bigID=big_geoid, smallID=small_geoid, 
            smallPopCol=population, lookup=lookupTable)
        basicDF['CD'] = [roundedValues[x] for x in basicDF[basic_geoid]]
        if 'Null' in basicDF['CD'].tolist():
            print("WARNING: the following chain units were not aligned with any bigger units:")
            print(mylist)
            print("Check your CRS of each shapefile to see if the maps are aligned")

        basicDF.to_file("Rounded.shp")
        print("\nwrote to new shapefile: Rounded.shp\n")
        roundoff_report("Roundoff.html", bigDF, basicDF,
                big_geoid, basic_geoid, lookupTable)
        print("\nReport written to file: Roundoff.html\n")
        page.destroyall()

    elif page.title == "Merge & Report":
        voteColumns = [x.strip() for x in str(page.basicShapefileCols.get()).split(",")]

        sname = os.path.basename(page.basicUnits.split('.')[0])
        outputName = f"Report_on_{sname}.html"

        generic_shapefile_report(outputName, dataFrame=[sname, basicDF],
                idColumn=basic_geoid, voteColumns=voteColumns, electionDicts=None)
        print(f"\nReport written to file: {outputName}\n")
        page.destroyall()

    else:
        raise Exception("ERROR: Invalid page")


class ApplicationTab(ttk.Frame):
    '''
    A child class of the tkk Frame which makes a tab in an application.
    User input fields correspond to object variables.
    '''

    def passFunc(self):
        pass

    def clear_basic_idprompt(self, event):
        if self.geoid1.get() == "Column Name":
            self.geoid1.delete(0, tk.END)
    
    def clear_big_idprompt(self, event):
        if self.geoid2.get() == "Column Name":
            self.geoid2.delete(0, tk.END)

    def clear_vote_column(self, event):
        if self.voteEntry.get() == "Names of columns to prorate":
            self.voteEntry.delete(0, tk.END)

    def clear_pop_column(self, event):
        if self.popEntry.get() == "Population column Name":
            self.popEntry.delete(0, tk.END)

    def clear_small_idprompt(self, event):
        if self.geoid3.get() == "Column Name":
            self.geoid3.delete(0, tk.END)
 
    def clear_basic_csvidprompt(self, event):
        if self.basicMergEntry.get() == "CSV ID":
            self.basicMergeEntry.delete(0, tk.END)

    def clear_big_csvidprompt(self, event):
        if self.bigMergeEntry.get() == "CSV ID":
            self.bigMergeEntry.delete(0, tk.END)

    def clear_small_csvidprompt(self, event):
        if self.smallMergEntry.get() == "CSV ID":
            self.smallMergeEntry.delete(0, tk.END)

    def selectPath(self, selfUnitsPath, selfUnitsButton):
        setattr(self, selfUnitsPath, filedialog.askopenfilename())
        selectedFile = getattr(self, selfUnitsPath)
        getattr(self, selfUnitsButton).configure(text='...'+selectedFile[-8:])
        print("File selected : " + selectedFile)
    
    def enable_basic_csv(self):
        if self.basicCheck.get():
            self.basicMergeEntry.configure(state='normal')
            self.basicMerge.configure(state='normal')
        else:
            self.basicMergeEntry.configure(state='disabled')
            self.basicMerge.configure(state='disabled')

    def enable_big_csv(self):
        if self.bigCheck.get():
            self.bigMergeEntry.configure(state='normal')
            self.bigMerge.configure(state='normal')
        else:
            self.bigMergeEntry.configure(state='disabled')
            self.bigMerge.configure(state='disabled')

    def enable_small_csv(self):
        if self.smallCheck.get():
            self.smallMerge.configure(state='normal')
            self.smallMerge.configure(state='normal')
        else:
            self.smallMerge.configure(state='disabled')
            self.smallMerge.configure(state='disabled')

    def destroyall(self):
        self.root.destroy()
        exit(0)

    def __init__(self, title, root):
        tk.Frame.__init__(self, root)

        self.title = title
        self.root = root

        self.basicUnits = ''
        self.biggerUnits = ''
        self.smallestUnits = ''
        self.basicMergePath = ''
        self.biggestMergePath = ''
        self.smallestMergePath = ''

        # These subframes are the four rows.
        self.num1 = tk.Frame(self)
        self.num2 = tk.Frame(self)
        self.num3 = tk.Frame(self)
        self.num4 = tk.Frame(self)
        self.optFloat = tk.Frame(self)

        # 1.0 TITLE ROW
        self.topLabel = tk.Label(self.num1,
                text="Preprocess that Data!", anchor=tk.W, font="Helvetica 30")

        # 2.0 SELECT UNITS ROW (title)
        self.num2_1 = tk.Frame(self.num2)
        self.selectLabel = tk.Label(self.num2_1,
                text="SELECT UNITS (shapefile format)",
                anchor=tk.W, font="Helvetica 14")

        # 2.1 SELECT UNITS ROW (basic)
        self.num2_2 = tk.Frame(self.num2)
        self.basicf1 = tk.Frame(self.num2_2, bg=basicColor)
        self.basicLabel = tk.Label(self.num2_2, bg=basicColor,
                fg=clearColor, text="basic chain units")
        self.geoid1 = tk.Entry(self.basicf1, width=10)
        self.basic = tk.Button(self.basicf1, text="Browse",
                     command=partial(self.selectPath,
                         'basicUnits', "basic"), height=1, width=8)

        # 2.2 SELECT UNITS ROW (big)
        self.num2_3 = tk.Frame(self.num2)
        self.bigf1 = tk.Frame(self.num2_3, bg=bigColor)
        self.bigLabel = tk.Label(self.num2_3, bg=bigColor, fg=clearColor, text="")
        self.geoid2 = tk.Entry(self.bigf1, width=10)

        self.big = tk.Button(self.bigf1, text="Browse",
                     command=partial(self.selectPath, 'biggerUnits', "big"),
                     width=8, height=1)
        self.voteEntry = tk.Entry(self.num2_3, width=20)

        # 2.3 SELECT UNITS ROW (small)
        self.num2_4 = tk.Frame(self.num2)
        self.smallf1 = tk.Frame(self.num2_4, bg=smallColor)
        self.smallLabel = tk.Label(self.num2_4, bg=smallColor, fg=clearColor,
                text="(optional)units that align with both")
        self.geoid3 = tk.Entry(self.smallf1, width=10)

        self.small = tk.Button(self.smallf1, text="Browse",
                     command=partial(self.selectPath, 'smallestUnits', "small"),
                     width=8, height=1)
        self.popEntry = tk.Entry(self.num2_4, width=20)

        # 3.0 ADD CSV DATA (title)
        self.num3_1 = tk.Frame(self.num3)
        self.mergeLabel = tk.Label(self.num3_1,
                text="MERGE COLUMNS FROM .csv (all columns added to shapefile)",
                anchor=tk.W, font="Helvetica 14")

        # 3.1 ADD CSV DATA (basic)
        self.num3_2 = tk.Frame(self.num3)
        self.basicf2 = tk.Frame(self.num3_2, bg=lBasicColor)
        self.basicMergeEntry = tk.Entry(self.basicf2, width=10)
        self.basicMerge = tk.Button(self.basicf2, text="Browse",
                command=partial(self.selectPath, 'basicMergePath', 'basicMerge'),
                width=8, height=1)
        self.basicMergeLabel = ttk.Label(self.basicf2,
                text=self.basicMergePath,font=("Helvtica", 8))
        self.basicMergeEntry.configure(state='disabled')
        self.basicMerge.configure(state='disabled')

        self.basicCheck = tk.BooleanVar()
        self.csv1 = tk.Checkbutton(self.num3_2,
                text="add CSV data", variable=self.basicCheck,
                onvalue=True, offvalue=False, height=1, width=12, bg=lBasicColor, 
                command=self.enable_basic_csv)

        # 3.2 ADD CSV DATA (big)
        self.num3_3 = tk.Frame(self.num3)
        self.bigf2 = tk.Frame(self.num3_3, bg=lBigColor)
        self.bigMergeEntry = tk.Entry(self.bigf2, width=10)
        self.bigMerge = tk.Button(self.bigf2, text="Browse",
                command=partial(self.selectPath, 'biggestMergePath', 'bigMerge'),
                width=8, height=1)
        self.bigMergeLabel = ttk.Label(root,
                text =self.biggestMergePath,font=("Helvetica", 8))
        self.bigMergeEntry.configure(state='disabled')
        self.bigMerge.configure(state='disabled')

        self.bigCheck = tk.BooleanVar()
        self.csv2 = tk.Checkbutton(self.num3_3,
                text="add CSV data", variable=self.bigCheck,
                onvalue=True, offvalue=False, height=1, width=12, bg=lBigColor, 
                command=self.enable_big_csv)

        # 3.3 ADD CSV DATA (small)
        self.num3_4 = tk.Frame(self.num3)
        self.smallf2 = tk.Frame(self.num3_4, bg=lSmallColor)
        self.smallMergeEntry = tk.Entry(self.smallf2, width=10)
        self.smallMerge = tk.Button(self.smallf2, text="Browse",
                command=partial(self.selectPath, 'smallestMergePath', 'smallMerge'),
                width=8, height=1)
        self.smallMergeLabel = ttk.Label(root,
                text =self.smallestMergePath,font=("Helvetica", 8))
        self.smallMergeEntry.configure(state='disabled')
        self.smallMerge.configure(state='disabled')

        self.smallCheck = tk.BooleanVar()
        self.csv3 = tk.Checkbutton(self.num3_4,
                text="add CSV data", variable=self.smallCheck,
                onvalue=True, offvalue=False, height=1, width=12, bg=lSmallColor,
                command=self.enable_small_csv)

        # 4.0 PROCESS BUTTON
        self.num4_3 = tk.Frame(self.num4)

        self.basicShapefileCols = tk.Entry(self.optFloat, width=30)
        self.basicShapefileColText = tk.Label(self.optFloat,
                text="(Optional) vote columns to report on: ")

        # Creates the button to process and pass all variables
        self.b = tk.Button(self.num4_3, text=self.title + '!',
                width=15, command=partial(callback, self))
        
    
    def show(self):

        #ORGANIZE INTO ROWS
        # 1.0: TITLE ROW
        self.num1.place(relx=0, rely=0, relwidth=1, relheight=rowDepth[0])
        self.topLabel.place(relx=thirdsSep[0], rely=0, relwidth=1, relheight=1)


        if self.title != "Merge & Report":

            # 2.1 SELECT UNITS ROW (basic)
            self.num2.place(relx=0, rely=rowDepth[0],
                    relwidth=1, relheight=rowDepth[1] - rowDepth[0])
            self.num2_1.place(relx=0, rely=0, relwidth=1, relheight=.15)
            self.selectLabel.place(relx=thirdsSep[0], rely=0, relwidth=1, relheight=1)

            self.num2_2.place(relx=thirdsSep[0], rely=.15,
                    relwidth=thirdsLen, relheight=.85)
            self.basicf1.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.basicLabel.place(relx=0, rely=0)
            self.geoid1.insert(tk.END, "Column Name")
            self.geoid1.bind("<Key>", self.clear_basic_idprompt)
            self.geoid1.place(relx=.5+offset, rely=.33)
            self.basic.place(relx=offset, rely=.33)

            # 2.2 SELECT UNITS ROW (big)
            self.num2_3.place(relx=thirdsSep[2], rely=.15,
                    relwidth=thirdsLen, relheight=.85)
            self.bigf1.place(relx=0, rely=0, relwidth=1, relheight=1)
            if self.title == "Prorate":
                self.bigLabel.configure(text="units with data to prorate")
            elif self.title == "Roundoff":
                self.bigLabel.configure(text="congressional districts to round")
            self.bigLabel.place(relx=0, rely=0)
            self.geoid2.insert(tk.END, "Column Name")
            self.geoid2.bind("<Key>", self.clear_big_idprompt)
            self.geoid2.place(relx=.5+offset, rely=.33)
            if self.title == "Prorate":
                self.voteEntry.insert(tk.END, "Names of columns to prorate")
                self.voteEntry.bind("<Key>", self.clear_vote_column)
                self.voteEntry.place(relx=offset, rely=.66)
            self.big.place(relx=offset, rely=.33)

            # 2.3 SELECT UNITS ROW (small)
            self.num2_4.place(relx=thirdsSep[4], rely=.15,
                    relwidth=thirdsLen, relheight=.85)
            self.smallf1.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.smallLabel.place(relx=0, rely=0)
            self.geoid3.insert(tk.END, "Column Name")
            self.geoid3.bind("<Key>", self.clear_small_idprompt)
            self.geoid3.place(relx=.5+offset, rely=.33)
            self.popEntry.insert(tk.END, "Population column Name")
            self.popEntry.bind("<Key>", self.clear_pop_column)
            self.small.place(relx=offset, rely=.33)
            self.popEntry.place(relx=offset,rely=.66)

            # 3
            self.num3.place(relx=0, rely=rowDepth[2],
                    relwidth=1, relheight=rowDepth[3] - rowDepth[2])
            self.num3_1.place(relx=0, rely=0, relwidth=1, relheight=.15)
            self.mergeLabel.place(relx=thirdsSep[0], rely=0, relwidth=1, relheight=1)
            self.num3_2.place(relx=thirdsSep[0], rely=.15,
                    relwidth=thirdsLen, relheight=.85)
            self.basicf2.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.basicMergeEntry.configure(state='normal')
            self.basicMergeEntry.insert(tk.END, "CSV ID")
            self.basicMergeEntry.configure(state='disabled')
            self.basicMergeEntry.bind("<Key>", self.clear_basic_csvidprompt)
            self.basicMergeEntry.place(relx=.5+offset, rely=.55)
            self.basicMerge.place(relx=offset, rely=.55)
            self.csv1.pack()
            self.csv1.place(relx=0, rely=.15)

            self.num3_3.place(relx=thirdsSep[2], rely=.15,
                    relwidth=thirdsLen, relheight=.85)
            self.bigf2.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.bigMergeEntry.configure(state='normal')
            self.bigMergeEntry.insert(tk.END, "CSV ID")
            self.bigMergeEntry.configure(state='disabled')
            self.bigMergeEntry.bind("<Key>", self.clear_big_csvidprompt)
            self.bigMergeEntry.place(relx=.5+offset, rely=.55)
            self.bigMerge.place(relx=offset, rely=.55)
            self.csv2.pack()
            self.csv2.place(relx=0, rely=.15)

            self.num3_4.place(relx=thirdsSep[4], rely=.15,
                    relwidth=thirdsLen, relheight=.85)
            self.smallf2.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.smallMergeEntry.configure(state='normal')
            self.smallMergeEntry.insert(tk.END, "CSV ID")
            self.smallMergeEntry.configure(state='disabled')
            self.smallMergeEntry.bind("<Key>", self.clear_small_csvidprompt)
            self.smallMergeEntry.place(relx=.5+offset, rely=.55)
            self.smallMerge.place(relx=offset, rely=.55)
            self.csv3.pack()
            self.csv3.place(relx=0, rely=.15)

        elif self.title == "Merge & Report":

            # 2.1 SELECT UNITS ROW (basic)
            self.num2.place(relx=0, rely=rowDepth[0],
                    relwidth=.5, relheight=rowDepth[1] - rowDepth[0])
            self.num2_1.place(relx=0, rely=0, relwidth=1, relheight=.15)
            self.selectLabel.place(relx=thirdsSep[0], rely=0, relwidth=1, relheight=1)

            self.num2_2.place(relx=thirdsSep[0], rely=.15,
                    relwidth=1 - 2 * thirdsSep[0], relheight=.85)
            self.basicf1.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.basicLabel.place(relx=0, rely=0)
            self.geoid1.insert(tk.END, "Column Name")
            self.geoid1.bind("<Key>", self.clear_basic_idprompt)
            self.geoid1.place(relx=.5+offset, rely=.33)
            self.basic.place(relx=offset, rely=.33)

            # 3
            self.num3.place(relx=.5, rely=rowDepth[0],
                    relwidth=.5, relheight=rowDepth[1] - rowDepth[0])
            self.num3_1.place(relx=0, rely=0, relwidth=1, relheight=.15)
            self.mergeLabel.configure(text="MERGE CSV FILE")
            self.mergeLabel.place(relx=thirdsSep[0], rely=0, relwidth=1, relheight=1)
            self.num3_2.place(relx=thirdsSep[0], rely=.15,
                    relwidth=thirdsSep[-1] - thirdsSep[0], relheight=.85)
            self.basicf2.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.basicMergeEntry.configure(state='normal')
            self.basicMergeEntry.insert(tk.END, "CSV ID")
            self.basicMergeEntry.configure(state='disabled')
            self.basicMergeEntry.bind("<Key>", self.clear_basic_csvidprompt)
            self.basicMergeEntry.place(relx=.5+offset, rely=.55)
            self.basicMerge.place(relx=offset, rely=.55)
            self.csv1.pack()
            self.csv1.place(relx=0, rely=.15)

            self.optFloat.place(relx=thirdsSep[0], rely = rowDepth[2],
                    relwidth=1 - 2 * thirdsSep[0], relheight=rowDepth[3] - rowDepth[2])
            self.optFloat.configure(bg=smallColor)
            self.basicShapefileColText.configure(fg=clearColor, bg=smallColor)
            self.basicShapefileColText.place(relx=offset, rely=.25)
            self.basicShapefileCols.place(relx=.5+offset, rely=.25)

        # 4
        self.num4.place(relx=0, rely=rowDepth[3], relwidth=1,
                relheight=rowDepth[4] - rowDepth[3])
        self.num4_3.place(relx=1 - 1.5 * thirdsLen, rely=0,
                relwidth=1.5 * thirdsLen, relheight=1)
        self.b.place(relx=.5, rely=0)

def demo():
    root = tk.Tk()
    root.title("Preprocessing Data!")
    root.geometry("x".join([str(x) for x in windowSize]))

    nb = ttk.Notebook(root)

    page1 = ApplicationTab("Prorate", nb)
    page1.show()

    page2 = ApplicationTab("Roundoff", nb)
    page2.show()

    page3 = ApplicationTab("Merge & Report", nb)
    page3.show()

    nb.add(page1, text='Prorate')
    nb.add(page2, text='Roundoff')
    nb.add(page3, text='Merge & Report')

    nb.pack(expand=1, fill="both")

    root.mainloop()

if __name__ == "__main__":
    demo()
