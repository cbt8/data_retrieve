# data_retrieve

#This .ipynb notebook is separated into five working parts, one for each school that is complete: HBS, Wharton, Stanford, Haas, and University of Michigan Ross. 
Two other schools are partially complete. I have not included these here. 

#Data is saved into dataframes, then concatenated and loaded into MongoDB. The output is the MongoDB collection with courses and descriptions. 
Some descriptions are arrays themselves, with one further level in the hierarchy.

Note: This takes quite a long time to run (about 5-6 minutes on my machine). I have been running the .py file instead of the .ipynb,
because it is a bit faster. 

3/12/19 update:

Quite a lot of new work. There is a UI now, which can be accessed by starting mongoDB, running the collected_data_retrieve.py code,
after completion prints, running the app.py code, and the going to the local server created from this last piece (http://127.0.0.1:5000/ is the default.)

Please enjoy, suggestions are welcome.

#Thanks again. 
