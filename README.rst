===================
Preprocessing DATA!
===================

This code is for preprocessing shapefiles to make them amenable to the 
RunDMCMC project. 
Currently supported functionality includes: 

+ Generating a quick report on shapefiles including column data  and stats 
on the underlying geographic units

+ Proration: the process of applying voting/demographic data from one 
set of geographic units (e.g. counties) to another (e.g. precincts). 
This is done proportionally to either the area of overlap, or the 
population in the overlap between geographic units. 

+ Roundoff: When a districting plan does not respect precinct/county lines, 
this process wiggles the boundaries of the districts until they do align. 


Getting the code
================
This code uses geopandas, pandas, matplotlib, tkInter, and numpy. Prior to 
downloading and attempting to run, all of these libaries will need to be 
installed. After this, clone/download the repository wherever to a useful 
location for accessing.

NOTE: this code produces reports for each process, as well as 
new shapefiles with added data if either proration or roundoff is 
used. These are automatically stored in the Preprocessing/ directory. 


Using in an interactive python session
======================================

To use this code for any of the above options, open a terminal, 
navigate to the Preprocessing folder in terminal, and type 
.. code-block:: python
    python main.py
This launches an interactive prompt with 3 tabs, one for 
each of the proeccesses that can be done. 


.. Preprocessing a shapefile: merging csv data, collecting column information, and reporting
.. -----------------------------------------------------------------------------------------


.. Roundoff: merging congressional district Data from one shapefile to another
.. ---------------------------------------------------------------------------


.. Prorating Data from one shapefile to another
.. --------------------------------------------

