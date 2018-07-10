import os
import numpy as np
import pandas as pd
import geopandas as gp
import tkinter as tk

from functools import partial

from tkinter import ttk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

from prorationAndRoundoff import prorateWithDFs, roundoffWithDFs, getLookupTable, getOverlayBetweenBasicAndLargeBySmall
from gen_report import prorate_and_roundoff_report, multifile_report

windowSize = [800, 425]

'''
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
'''

num_cols=3
num_rows=4
offset = 0.03
inset_proportion=.1
# Grid Layout
rowDepth=[inset_proportion + x * (1.0 / num_rows + y * offset) for y in [1, 3] for x in range(num_rows)]
colDepth=[inset_proportion + x * (1.0 / num_cols + y * offset) for y in [0, 2] for x in range(num_cols)]
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

    basicOutputFileName="basic"

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

    reportOutputFileName=[]
    
    if page.title == 'Prorate':
        p=True
        page.lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, small_geoid, population, basic_geoid, big_geoid, voting)
        basicOutputFileName += "Prorated"
        reportOutputFileName=["Prorated"]
        proratedValues = prorateWithDFs(bigDF, basicDF, smallDF, big_geoid, basic_geoid, small_geoid, population, voting, lookupTable)

        for i, c in enumerate(voting):
            basicDF[c] = [proratedValues[x][i] for x in basicDF[basic_geoid]]
    elif page.title == 'Roundoff':
        r=True
        if page.lookupTable is None:
            lookupTable = getOverlayBetweenBasicAndLargeBySmall(smallDF, basicDF, bigDF, small_geoid, basic_geoid, big_geoid, voting)
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
    else:
        raise Exception("ERROR: Invalid page")


    basicDF.to_file(basicOutputFileName+".shp")
    print("wrote to new shapefile: %s"%basicOutputFileName+".shp")

    # output data for report generation
    if len(reportOutputFileName) < 1:
        names = [x for x in [biggerUnits, basicUnits, smallestUnits] if x != '']
        cleaned_names = [os.path.basename(x).split(".")[0] for x in names]

        reportOutputFileName = "_and_".join(cleaned_names)+"_report.pdf"
        input_list = []
        if biggerUnits != '':
            mydict={"filename":biggerUnits, "idcolumn":big_geoid}
            if voting is not None:
                mydict["votecolumns"] = voting
            input_list.append(mydict)
        if basicUnits != '':
            input_list.append({"filename":basicUnits, "idcolumn":basic_geoid})
        if smallestUnits != '':
            mydict = {"filename":smallestUnits, "idcolumn":small_geoid}
            if page.popcolumn is not None:
                mydict["popcolumn"] = population
            input_list.append(mydict)

        multifile_report(reportOutputFileName, input_list)
    
    else:
        reportOutputFileName = "_and_".join(reportOutputFileName)+"_report.pdf"
        prorate_and_roundoff_report(
                reportOutputFileName=reportOutputFileName,
                biggerUnits=biggerUnits, bigDF=bigDF, big_geoid=big_geoid,
                basicUnits=basicOutputFileName+".shp", basicDF=basicDF, basic_geoid=basic_geoid,
                smallestUnits=smallestUnits, smallDF=smallDF, small_geoid=small_geoid,
                population=population,
                votes=voting,
                prorated=(page.title == 'Prorate'),
                rounded=(page.title == 'Roundoff'),
                lookupTable=lookupTable)



def selectBasicMerge():
    '''
    Allows the user to browse for a file to merge to basic units.
    :return: Filepath of the csv with data.
    '''
    global basicMergePath
    basicMergePath = filedialog.askopenfilename()
    print("file selected: " + basicMergePath)

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

    def selectPath(self, selfUnitsPath):
        setattr(self, selfUnitsPath, filedialog.askopenfilename())
        print("File selected : " + getattr(self, selfUnitsPath))
    
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
        self.selectLabel = tk.Label(self.num2_1, text="SELECT UNITS", anchor=tk.W, font="Helvetica 14")

        # 2.1 SELECT UNITS ROW (basic)
        self.num2_2 = tk.Frame(self.num2)
        self.basicf1 = tk.Frame(self.num2_2, bg=basicColor)
        self.geoid1 = tk.Entry(self.basicf1, width=10)
        self.basic = tk.Button(self.basicf1, text="Browse",
                     command=partial(self.selectPath, 'basicUnits'), height=1, width=10)

        # 2.2 SELECT UNITS ROW (big)
        self.num2_3 = tk.Frame(self.num2)
        self.bigf1 = tk.Frame(self.num2_3, bg=bigColor)
        self.geoid2 = tk.Entry(self.bigf1, width=10)
        
        self.big = tk.Button(self.bigf1, text="Browse",
                     command=partial(self.selectPath, 'biggerUnits'), width=10, height=1)
        self.voteEntry = tk.Entry(self.num2_3, width=10)

        # 2.3 SELECT UNITS ROW (small)
        self.num2_4 = tk.Frame(self.num2)
        self.smallf1 = tk.Frame(self.num2_4, bg=smallColor)
        self.geoid3 = tk.Entry(self.smallf1, width=10)

        self.small = tk.Button(self.smallf1, text="Browse",
                     command=partial(self.selectPath, 'smallestUnits'), width=10, height=1)
        self.popEntry = tk.Entry(self.num2_4, width=10)
        

        # 3.0 ADD CSV DATA (title)
        self.num3_1 = tk.Frame(self.num3)
        self.mergeLabel = tk.Label(self.num3_1, text="MERGE COLUMNS FROM .csv", anchor=tk.W, font="Helvetica 14")

        # 3.1 ADD CSV DATA (basic)
        self.num3_2 = tk.Frame(self.num3)
        self.basicf2 = tk.Frame(self.num3_2, bg=lBasicColor)
        self.basicMergeEntry = tk.Entry(self.basicf2, width=10)
        self.basicMerge = tk.Button(self.basicf2, text="Browse", command=selectBasicMerge, width=10, height=1)
        self.basicMergeLabel = ttk.Label(self.basicf2, text =self.basicMergePath,font=("Helvtica", 10))
        self.basicMergeEntry.configure(state='disabled')
        self.basicMerge.configure(state='disabled')
        
        self.basicCheck = tk.BooleanVar()
        self.csv1 = tk.Checkbutton(self.num3_2, text="add CSV data", variable=self.basicCheck,
                onvalue=True, offvalue=False, height=1, width=14, bg=basicColor, 
                command=self.enable_basic_csv)

        # 3.2 ADD CSV DATA (big)
        self.num3_3 = tk.Frame(self.num3)
        self.bigf2 = tk.Frame(self.num3_3, bg=lBigColor)
        self.bigMergeEntry = tk.Entry(self.bigf2, width=10)
        self.bigMerge = tk.Button(self.bigf2, text="Browse", command=selectBiggestMerge, width=10, height=1)
        self.bigMergeLabel = ttk.Label(root, text =self.biggestMergePath,font=("Helvetica", 10))
        self.bigMergeEntry.configure(state='disabled')
        self.bigMerge.configure(state='disabled')

        self.bigCheck = tk.BooleanVar()
        self.csv2 = tk.Checkbutton(self.num3_3, text="add CSV data", variable=self.bigCheck,
                onvalue=True, offvalue=False, height=1, width=14, bg=bigColor, 
                command=self.enable_big_csv)

        # 3.3 ADD CSV DATA (small)
        self.num3_4 = tk.Frame(self.num3)
        self.smallf2 = tk.Frame(self.num3_4, bg=lSmallColor)
        self.smallMergeEntry = tk.Entry(self.smallf2, width=10)
        self.smallMerge = tk.Button(self.smallf2, text="Browse", command=selectSmallestMerge, width=10, height=1)
        self.smallMergeLabel = ttk.Label(root, text =self.smallestMergePath,font=("Helvetica", 10))
        self.smallMergeEntry.configure(state='disabled')
        self.smallMerge.configure(state='disabled')

        self.smallCheck = tk.BooleanVar()
        self.csv3 = tk.Checkbutton(self.num3_4, text="add CSV data", variable=self.smallCheck,
                onvalue=True, offvalue=False, height=1, width=14, bg=smallColor, 
                command=self.enable_small_csv)
        
        # 4.0 PROCESS BUTTON
        self.num4_3 = tk.Frame(self.num4, bg=columnNamesColor)
        self.processLabel = tk.Label(self.num4_3, text="ANALYSIS", anchor=tk.W, font="Helvetica 14", bg=columnNamesColor)
        
        # Creates the button to process and pass all variables
        self.b = tk.Button(self.num4_3, text="Process", width=10, command=partial(callback, self))
        
    
    def show(self):

        #ORGANIZE INTO ROWS
        #self.num1.pack(side='top', fill='x', expand=False)
        #self.num2.pack(side='top', fill='both', expand=True)
        #self.num3.pack(side='top', fill='both', expand=True)
        #self.num4.pack(side='top', fill='both', expand=True)
        # 1.0: TITLE ROW
        self.num1.place(x=0, y=0, relwidth=1, relheight=1/(num_rows+1))
        self.topLabel.place(relx=thirdsSep[0], y=0, relwidth=1)

        # 2.1 SELECT UNITS ROW (basic)
        self.num2.place(relx=0, rely=rowDepth[0]+offset, relwidth=1, relheight=1/(num_rows+1))
        self.num2_1.place(relx=0, rely=0, relwidth=1, relheight=0.25)
        self.selectLabel.place(relx=thirdsSep[0], rely=0, relwidth=1)
        
        self.num2_2.place(relx=thirdsSep[0], rely=.25, relwidth=thirdsLen, relheight=0.75)
        self.basicf1.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.geoid1.insert(tk.END, "Chain Units ID")
        self.geoid1.bind("<Button-1>", self.clear_basic_idprompt)
        self.geoid1.place(relx=offset, rely=0.15)
        self.basic.place(relx=0.5+offset, rely=0.15)

        # 2.2 SELECT UNITS ROW (big)
        self.num2_3.place(relx=thirdsSep[2], rely=.25, relwidth=thirdsLen, relheight=0.75)
        self.bigf1.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.geoid2.insert(tk.END, "Big Units ID")
        self.geoid2.bind("<Button-1>", self.clear_big_idprompt)
        self.geoid2.place(relx=offset, rely=0.15)
        self.voteEntry.insert(tk.END, "Election Column Name")
        self.voteEntry.bind("<Button-1>", self.clear_vote_column)
        self.big.place(relx=0.5+offset, rely=0.15)
        self.voteEntry.place(relx=offset, rely=.55)

        # 2.3 SELECT UNITS ROW (small)
        self.num2_4.place(relx=thirdsSep[4], rely=.25, relwidth=thirdsLen, relheight=0.75)
        self.smallf1.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.geoid3.insert(tk.END, "Small Units ID")
        self.geoid3.bind("<Button-1>", self.clear_small_idprompt)
        self.geoid3.place(relx=offset, rely=0.15)
        self.popEntry.insert(tk.END, "Population Column Name")
        self.popEntry.bind("<Button-1>", self.clear_pop_column)
        self.small.place(relx=0.5+offset, rely=0.15)
        self.popEntry.place(relx=offset,rely=.55)

        # 3
        self.num3.place(relx=0, rely=rowDepth[1], relwidth=1, relheight=1/(num_rows+1))
        self.num3_1.place(relx=0, rely=0, relwidth=1, relheight=0.25)
        self.mergeLabel.place(relx=thirdsSep[0], rely=0, relwidth=1)
        self.num3_2.place(relx=thirdsSep[0], rely=rowDepth[1]-2*offset, relwidth=thirdsLen, relheight=0.75)
        self.basicf2.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.basicMergeEntry.insert(tk.END, "Basic Units ID")
        self.basicMergeEntry.bind("<Button-1>", self.clear_basic_csvidprompt)
        self.basicMergeEntry.place(relx=offset, rely=0.15)
        self.basicMerge.place(relx=0.5+offset, rely=0.15)
        self.csv1.pack()
        self.csv1.place(relx=offset, rely=.55)

        self.num3_3.place(relx=thirdsSep[2], rely=rowDepth[1]-2*offset, relwidth=thirdsLen, relheight=0.75)
        self.bigf2.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bigMergeEntry.insert(tk.END, "Basic Units ID")
        self.bigMergeEntry.bind("<Button-1>", self.clear_big_csvidprompt)
        self.bigMergeEntry.place(relx=offset, rely=0.15)
        self.bigMerge.place(relx=0.5+offset, rely=0.15)
        self.csv2.pack()
        self.csv2.place(relx=offset, rely=.55)

        self.num3_4.place(relx=thirdsSep[4], rely=rowDepth[1]-2*offset, relwidth=thirdsLen, relheight=0.75)
        self.smallf2.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.smallMergeEntry.insert(tk.END, "Basic Units ID")
        self.smallMergeEntry.bind("<Button-1>", self.clear_small_csvidprompt)
        self.smallMergeEntry.place(relx=offset, rely=0.15)
        self.smallMerge.place(relx=0.5+offset, rely=0.15)
        self.csv3.pack()
        self.csv3.place(relx=offset, rely=.55)

        # 4
        self.num4.place(relx=0, rely=rowDepth[2], relwidth=1, relheight=1/(num_rows))
        self.num4_3.place(relx=thirdsSep[4], rely=0, relwidth=thirdsLen, relheight=1)
        self.processLabel.place(relx=0, rely=0, relwidth=1)
        self.b.place(relx=.5, rely=.75)

def demo():
    root = tk.Tk()
    root.title("ttk.Notebook")
    root.geometry("x".join([str(x) for x in windowSize]))

    nb = ttk.Notebook(root)

    page1 = ApplicationTab("Prorate", nb)
    page1.show()

    page2 = ApplicationTab("Roundoff", nb)
    page2.show()

    nb.add(page1, text='Process')
    nb.add(page2, text='Roundoff')

    nb.pack(expand=1, fill="both")

    root.mainloop()

if __name__ == "__main__":
    demo()