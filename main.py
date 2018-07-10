import os
import numpy as np
import pandas as pd
import geopandas as gp
import tkinter as tk

from functools import partial

from tkinter import ttk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

from prorationAndRoundoff import prorateWithDFs, roundoffWithDFs, getOverlayBetweenBasicAndLargeBySmall
from gen_report import prorate_report, roundoff_report

windowSize = [800, 425]

num_cols=3
num_rows=3
offset = 0.01
inset_proportion=.1
# Grid Layout
rowDepth = [0.2, 0.5, .6, 0.9, 0.99]

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
    
    # Historically, this is where top was destroyed.
    # top.destroy()

    # now read files into geodataframes and join csvs if flagged
    if page.basicUnits != '':
        basicDF = gp.read_file(page.basicUnits)
        if merge_basic_col != '' and page.basicMergePath != '':
            basicMerge = pd.read_csv(page.basicMergePath)
            basicDF = basicDF.merge(basicMerge, left_on=basic_geoid, right_on=merge_basic_col)
    else:
        raise Exception("ERROR: Must enter a valid file name for basic units")

    if page.biggerUnits != '':
        bigDF = gp.read_file(page.biggerUnits)
        if merge_biggest_col != '' and page.biggestMergePath != '':
            bigMerge = pd.read_csv(page.biggestMergePath)
            bigDF = bigDF.merge(bigMerge, left_on=big_geoid, right_on=merge_biggest_col)

    if len(page.smallestUnits)>0:
        smallDF = gp.read_file(page.smallestUnits)
        if merge_smallest_col != '' and page.smallestMergePath != '':
            smallMerge = pd.read_csv(page.smallestMergePath)
            smallDF = bigDF.merge(smallMerge, left_on=small_geoid, right_on=merge_smallest_col)
    else:
        smallDF = None
    lookupTable = None

    if page.title == 'Prorate':
        lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, small_geoid, population, basic_geoid, big_geoid)
        proratedValues = prorateWithDFs(bigDF, basicDF, big_geoid, basic_geoid, voting, lookupTable, prorateCol='pop')

        for i, c in enumerate(voting):
            basicDF[c] = [proratedValues[x][i] for x in basicDF[basic_geoid]]

        basicDF.to_file("Prorated.shp")
        print("\nwrote to new shapefile: Prorated.shp\n")

        basicname = os.path.basename(page.basicUnits.split('.')[0])
        bigname = os.path.basename(page.biggerUnits.split('.')[0])
        prorate_report("Proration.html", [bigname, bigDF], [basicname, basicDF], smallDF, big_geoid, basic_geoid, small_geoid, population, voteColumns=voting)
        print("\nReport written to file: Proration.html\n")

    elif page.title == 'Roundoff':
        if lookupTable is None:
            lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, small_geoid, population, basic_geoid, big_geoid)
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

        basicDF.to_file("Rounded.shp")
        print("\nwrote to new shapefile: Rounded.shp\n")

        roundoff_report("Roundoff.html", bigDF, basicDF, big_geoid, basic_geoid)
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
        self.geoid1.delete(0, tk.END)
    
    def clear_big_idprompt(self, event):
        self.geoid2.delete(0, tk.END)

    def clear_vote_column(self, event):
        self.voteEntry.delete(0, tk.END)

    def clear_pop_column(self, event):
        self.popEntry.delete(0, tk.END)

    def clear_small_idprompt(self, event):
        self.geoid3.delete(0, tk.END)
 
    def clear_basic_csvidprompt(self, event):
        self.basicMergeEntry.delete(0, tk.END)

    def clear_big_csvidprompt(self, event):
        self.bigMergeEntry.delete(0, tk.END)

    def clear_small_csvidprompt(self, event):
        self.smallMergeEntry.delete(0, tk.END)

    def selectPath(self, selfUnitsPath, selfUnitsButton):
        setattr(self, selfUnitsPath, filedialog.askopenfilename())
        selectedFile = getattr(self, selfUnitsPath)
        getattr(self, selfUnitsButton).configure(text='...'+selectedFile[-10:])
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

    def __init__(self, title, root):
        tk.Frame.__init__(self, root)
        
        self.title = title
        
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

        # 1.0 TITLE ROW
        self.topLabel = tk.Label(self.num1, text="Preprocess that Data!", anchor=tk.W, font="Helvetica 30")

        # 2.0 SELECT UNITS ROW (title)
        self.num2_1 = tk.Frame(self.num2)
        self.selectLabel = tk.Label(self.num2_1, text="SELECT UNITS (shapefile format)", anchor=tk.W, font="Helvetica 14")

        # 2.1 SELECT UNITS ROW (basic)
        self.num2_2 = tk.Frame(self.num2)
        self.basicf1 = tk.Frame(self.num2_2, bg=basicColor)
        self.basicLabel = tk.Label(self.num2_2, bg=basicColor, fg=clearColor, text="basic chain units")
        self.geoid1 = tk.Entry(self.basicf1, width=10)
        self.basic = tk.Button(self.basicf1, text="Browse",
                     command=partial(self.selectPath, 'basicUnits', "basic"), height=1, width=8)

        # 2.2 SELECT UNITS ROW (big)
        self.num2_3 = tk.Frame(self.num2)
        self.bigf1 = tk.Frame(self.num2_3, bg=bigColor)
        self.bigLabel = tk.Label(self.num2_3, bg=bigColor, fg=clearColor, text="")
        self.geoid2 = tk.Entry(self.bigf1, width=10)
        
        self.big = tk.Button(self.bigf1, text="Browse",
                     command=partial(self.selectPath, 'biggerUnits', "big"), width=8, height=1)
        self.voteEntry = tk.Entry(self.num2_3, width=20)

        # 2.3 SELECT UNITS ROW (small)
        self.num2_4 = tk.Frame(self.num2)
        self.smallf1 = tk.Frame(self.num2_4, bg=smallColor)
        self.smallLabel = tk.Label(self.num2_4, bg=smallColor, fg=clearColor, text="(optional)units that align with both")
        self.geoid3 = tk.Entry(self.smallf1, width=10)

        self.small = tk.Button(self.smallf1, text="Browse",
                     command=partial(self.selectPath, 'smallestUnits', "small"), width=8, height=1)
        self.popEntry = tk.Entry(self.num2_4, width=20)
        

        # 3.0 ADD CSV DATA (title)
        self.num3_1 = tk.Frame(self.num3)
        self.mergeLabel = tk.Label(self.num3_1, text="MERGE COLUMNS FROM .csv (all columns of data will be added to shapefile)", anchor=tk.W, font="Helvetica 14")

        # 3.1 ADD CSV DATA (basic)
        self.num3_2 = tk.Frame(self.num3)
        self.basicf2 = tk.Frame(self.num3_2, bg=lBasicColor)
        self.basicMergeEntry = tk.Entry(self.basicf2, width=10)
        self.basicMerge = tk.Button(self.basicf2, text="Browse",
                command=partial(self.selectPath, 'basicMergePath', 'basicMerge'), width=8, height=1)
        self.basicMergeLabel = ttk.Label(self.basicf2, text=self.basicMergePath,font=("Helvtica", 8))
        self.basicMergeEntry.configure(state='disabled')
        self.basicMerge.configure(state='disabled')
        
        self.basicCheck = tk.BooleanVar()
        self.csv1 = tk.Checkbutton(self.num3_2, text="add CSV data", variable=self.basicCheck,
                onvalue=True, offvalue=False, height=1, width=12, bg=lBasicColor, 
                command=self.enable_basic_csv)

        # 3.2 ADD CSV DATA (big)
        self.num3_3 = tk.Frame(self.num3)
        self.bigf2 = tk.Frame(self.num3_3, bg=lBigColor)
        self.bigMergeEntry = tk.Entry(self.bigf2, width=10)
        self.bigMerge = tk.Button(self.bigf2, text="Browse",
                command=partial(self.selectPath, 'biggestMergePath', 'bigMerge'), width=8, height=1)
        self.bigMergeLabel = ttk.Label(root, text =self.biggestMergePath,font=("Helvetica", 8))
        self.bigMergeEntry.configure(state='disabled')
        self.bigMerge.configure(state='disabled')

        self.bigCheck = tk.BooleanVar()
        self.csv2 = tk.Checkbutton(self.num3_3, text="add CSV data", variable=self.bigCheck,
                onvalue=True, offvalue=False, height=1, width=12, bg=lBigColor, 
                command=self.enable_big_csv)

        # 3.3 ADD CSV DATA (small)
        self.num3_4 = tk.Frame(self.num3)
        self.smallf2 = tk.Frame(self.num3_4, bg=lSmallColor)
        self.smallMergeEntry = tk.Entry(self.smallf2, width=10)
        self.smallMerge = tk.Button(self.smallf2, text="Browse",
                command=partial(self.selectPath, 'smallestMergePath', 'smallMerge'), width=8, height=1)
        self.smallMergeLabel = ttk.Label(root, text =self.smallestMergePath,font=("Helvetica", 8))
        self.smallMergeEntry.configure(state='disabled')
        self.smallMerge.configure(state='disabled')

        self.smallCheck = tk.BooleanVar()
        self.csv3 = tk.Checkbutton(self.num3_4, text="add CSV data", variable=self.smallCheck,
                onvalue=True, offvalue=False, height=1, width=12, bg=lSmallColor, 
                command=self.enable_small_csv)
        
        # 4.0 PROCESS BUTTON
        self.num4_3 = tk.Frame(self.num4, bg=clearColor)
        #self.processLabel = tk.Label(self.num4_3, text="ANALYSIS", anchor=tk.W, font="Helvetica 14", bg=columnNamesColor)
        
        # Creates the button to process and pass all variables
        self.b = tk.Button(self.num4_3, text=self.title + '!', width=10, command=partial(callback, self))
        
    
    def show(self):

        #ORGANIZE INTO ROWS
        #self.num1.pack(side='top', fill='x', expand=False)
        #self.num2.pack(side='top', fill='both', expand=True)
        #self.num3.pack(side='top', fill='both', expand=True)
        #self.num4.pack(side='top', fill='both', expand=True)
        # 1.0: TITLE ROW
        self.num1.place(relx=0, rely=0, relwidth=1, relheight=rowDepth[0])
        self.topLabel.place(relx=thirdsSep[0], rely=0, relwidth=1, relheight=1)

        # 2.1 SELECT UNITS ROW (basic)
        self.num2.place(relx=0, rely=rowDepth[0], relwidth=1, relheight=rowDepth[1] - rowDepth[0])
        self.num2_1.place(relx=0, rely=0, relwidth=1, relheight=0.15)
        self.selectLabel.place(relx=thirdsSep[0], rely=0, relwidth=1, relheight=1)
        
        self.num2_2.place(relx=thirdsSep[0], rely=.15, relwidth=thirdsLen, relheight=0.85)
        self.basicf1.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.basicLabel.place(relx=0, rely=0)
        self.geoid1.insert(tk.END, "ID Column")
        self.geoid1.bind("<Button-1>", self.clear_basic_idprompt)
        self.geoid1.place(relx=0.5+offset, rely=0.33)
        self.basic.place(relx=offset, rely=0.33)

        # 2.2 SELECT UNITS ROW (big)
        self.num2_3.place(relx=thirdsSep[2], rely=.15, relwidth=thirdsLen, relheight=0.85)
        self.bigf1.place(relx=0, rely=0, relwidth=1, relheight=1)
        if self.title == "Prorate":
            self.bigLabel.configure(text="units with data to prorate")
        elif self.title == "Roundoff":
            self.bigLabel.configure(text="congressional districts to round")
        self.bigLabel.place(relx=0, rely=0)
        self.geoid2.insert(tk.END, "ID Column")
        self.geoid2.bind("<Button-1>", self.clear_big_idprompt)
        self.geoid2.place(relx=0.5+offset, rely=0.33)
        if self.title == "Prorate":
            self.voteEntry.insert(tk.END, "Vote columns to prorate")
            self.voteEntry.bind("<Button-1>", self.clear_vote_column)
            self.voteEntry.place(relx=offset, rely=.66)
        self.big.place(relx=offset, rely=0.33)

        # 2.3 SELECT UNITS ROW (small)
        self.num2_4.place(relx=thirdsSep[4], rely=.15, relwidth=thirdsLen, relheight=0.85)
        self.smallf1.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.smallLabel.place(relx=0, rely=0)
        self.geoid3.insert(tk.END, "ID Column")
        self.geoid3.bind("<Button-1>", self.clear_small_idprompt)
        self.geoid3.place(relx=0.5+offset, rely=0.33)
        self.popEntry.insert(tk.END, "Population column Name")
        self.popEntry.bind("<Button-1>", self.clear_pop_column)
        self.small.place(relx=offset, rely=0.33)
        self.popEntry.place(relx=offset,rely=.66)

        # 3
        self.num3.place(relx=0, rely=rowDepth[2], relwidth=1, relheight=rowDepth[3] - rowDepth[2])
        self.num3_1.place(relx=0, rely=0, relwidth=1, relheight=0.15)
        self.mergeLabel.place(relx=thirdsSep[0], rely=0, relwidth=1, relheight=1)
        self.num3_2.place(relx=thirdsSep[0], rely=.15, relwidth=thirdsLen, relheight=0.85)
        self.basicf2.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.basicMergeEntry.configure(state='normal')
        self.basicMergeEntry.insert(tk.END, "CSV ID")
        self.basicMergeEntry.configure(state='disabled')
        self.basicMergeEntry.bind("<Button-1>", self.clear_basic_csvidprompt)
        self.basicMergeEntry.place(relx=0.5+offset, rely=0.55)
        self.basicMerge.place(relx=offset, rely=0.55)
        self.csv1.pack()
        self.csv1.place(relx=0.0, rely=.15)

        self.num3_3.place(relx=thirdsSep[2], rely=.15, relwidth=thirdsLen, relheight=0.85)
        self.bigf2.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bigMergeEntry.configure(state='normal')
        self.bigMergeEntry.insert(tk.END, "CSV ID")
        self.bigMergeEntry.configure(state='disabled')
        self.bigMergeEntry.bind("<Button-1>", self.clear_big_csvidprompt)
        self.bigMergeEntry.place(relx=0.5+offset, rely=0.55)
        self.bigMerge.place(relx=offset, rely=0.55)
        self.csv2.pack()
        self.csv2.place(relx=0.0, rely=.15)

        self.num3_4.place(relx=thirdsSep[4], rely=.15, relwidth=thirdsLen, relheight=0.85)
        self.smallf2.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.smallMergeEntry.configure(state='normal')
        self.smallMergeEntry.insert(tk.END, "CSV ID")
        self.smallMergeEntry.configure(state='disabled')
        self.smallMergeEntry.bind("<Button-1>", self.clear_small_csvidprompt)
        self.smallMergeEntry.place(relx=0.5+offset, rely=0.55)
        self.smallMerge.place(relx=offset, rely=0.55)
        self.csv3.pack()
        self.csv3.place(relx=0.0, rely=.15)

        # 4
        self.num4.place(relx=0, rely=rowDepth[3], relwidth=1, relheight=rowDepth[4] - rowDepth[3])
        self.num4_3.place(relx=thirdsSep[4], rely=0, relwidth=thirdsLen, relheight=1)
        self.b.place(relx=.5, rely=0)

def demo():
    root = tk.Tk()
    root.title("ttk.Notebook")
    root.geometry("x".join([str(x) for x in windowSize]))

    nb = ttk.Notebook(root)

    page1 = ApplicationTab("Prorate", nb)
    page1.show()

    page2 = ApplicationTab("Roundoff", nb)
    page2.show()

    nb.add(page1, text='Prorate')
    nb.add(page2, text='Roundoff')

    nb.pack(expand=1, fill="both")

    root.mainloop()

if __name__ == "__main__":
    demo()
