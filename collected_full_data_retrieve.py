
# coding: utf-8

# In[9]:


from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import re
import pymongo
import numpy as np


# In[2]:


conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.curriculumDB
db.curriculum.delete_many({})
curriculum_collection = db.curriculumDB


# In[3]:


#First is HBS

source='https://www.hbs.edu/coursecatalog/indexcourse.html'

html = urlopen(str(source))
soup = BeautifulSoup(html, 'html.parser')

tdlist = soup.find_all('td')

reflist = []
for i in range(len(tdlist)):
    if str(tdlist[i])[:27] == '<td><a href="/coursecatalog':
        reflist.append(str(tdlist[i]))
    
#This code is necessary because HBS has course descriptions on different pages, rather than collected in one URL.

linklist = []
for i in range(len(reflist)):
    linklist.append(reflist[i][14:37])
    
#Creating a list of link extensions    
    
descraw = []

for i in range(len(linklist)):
    link = urlopen('https://www.hbs.edu/'+ linklist[i])
    descsoup = BeautifulSoup(link, 'html.parser')
    descraw.append(descsoup.findAll('p'))
    
#navigating to link extensions and retrieving course descriptions    


titlelist = []
for i in range(len(reflist)):
    titlelist.append(re.sub('<[^<]+?>', '', str(reflist[i]))) 
#titlelist


hbsdf = pd.DataFrame(titlelist, columns=["Course"])
hbsdf['Description'] = descraw
hbsdf['School'] = 'Harvard Business School'
hbsdf['Source'] = source

for i in range(len(hbsdf['Description'])):
    hbsdf['Description'][i]= re.sub('<[^<]+?>', '', str(hbsdf['Description'][i]))
    
    hbsdf['Source'][i] = 'https://www.hbs.edu/'+ linklist[i]

#This writes everything to a dataframe. Easy to export to excel. The original data is stored in a list, so it could
#easily be written to a different kind of object, but I have used dataframes here for convenience.


# In[4]:


#Next is Wharton. This was the first code that I wrote, so it is a bit clunkier. Also, this includes prerequisites. (Note: this is removed in current mongoDB version)
#I have decided to remove this from the final version, because it is outside the scope of the original project.

source='https://mgmt.wharton.upenn.edu/programs/mba/course-descriptions/'

html = urlopen(str(source))
soup = BeautifulSoup(html, 'html.parser')

full_text = soup.get_text()

title = soup.select('h3')
para = soup.select('p')

for i in range(len(title)):
    title[i] = re.sub('<[^<]+?>', '', str(title[i]))

#you can see here I am scrubbing everything unnecessarily early in the process. 

title1df = pd.DataFrame(title, columns=['Course'])

title1df['Source'] = source

#The above two sections are taking the raw course catalog and putting it into a dataframe. The below sections are removing the
#'prerequisites' columns. Because this comes from the original code, where I created an excel file with only course names, 
#there is some redundancy here. Keeping it in case the code comes in handy later. 

for i in range(len(title1df)):
    if i >0:
        title1df['Source'][i]= ''
    else:
        continue
        
prereq = []

for strong_tag in soup.find_all('strong'):
    prereq.append((strong_tag.text, strong_tag.next_sibling))
    
poplist = []
prereqlist = []

for i in range(len(para)):
    if str(para[i])[:11] == '<p><strong>':
        poplist.append(i)
    else:
        continue

newpara = []

for i in range(len(para)):
    if i in poplist:
        prereqlist.append(para[i])
    else:
        newpara.append(para[i])

        
#All of this is to fix the problem of classes without prerequisites. This is redundant, but the code is included here in 
#case it is useful for another school's formatting (all these websites have different formatting)

#Note: In the most recent version, this doesn't actually do anything, because I didn't include a prerequisites column. Doesn't change anything important in the code. 

fulldf = pd.DataFrame(title[:-3], columns= ['Course'])

fulldf['Source'] = source
fulldf['School'] = 'Wharton'

fulldf['Description'] = ''

for i in range(len(newpara)):
    fulldf['Description'][i]= re.sub('<[^<]+?>', '', str(newpara[i]))

newpara
fulldf['Prerequisites'] = ""       

for i in range(len(fulldf)):
    for j in range(len(poplist)):
        if i == poplist[j]:
            fulldf['Prerequisites'][i]= re.sub('<[^<]+?>', '', str(prereqlist[j]))
        else: continue   
fullcols = fulldf.columns.tolist()

newcols = ['Course','Description',  'Source', 'School']

whartondf = fulldf[newcols]


# In[5]:


#Stanford had problably the simplest, best-formatted website. Bless the people at Stanford who are running this website. 

source = 'https://exploredegrees.stanford.edu/graduateschoolofbusiness/#courseinventory'

html = urlopen(str(source))
soup = BeautifulSoup(html, 'html.parser')

#soup.find_all()
title = soup.select('strong')

for i in range(len(title)):
    title[i] = re.sub('<[^<]+?>', '', str(title[i]))
    
titlelist = []
desclist = []

for i in soup.findAll('p'):
    if str(i)[:28] == '<p class="courseblocktitle">':
        titlelist.append(i)
    
    elif str(i)[:27] == '<p class="courseblockdesc">':
        desclist.append(i)
        
        
#Below is simply to remove html tags from the text.
        
for i in range(len(title)):
    title[i] = re.sub('<[^<]+?>', '', str(title[i]))     
        
stanforddf = pd.DataFrame(titlelist, columns=["Course"])

stanforddf['Description'] = desclist

for i in range(len(stanforddf)):
    stanforddf['Course'][i] = re.sub('<[^<]+?>', '', str( stanforddf['Course'][i]))
    stanforddf['Description'][i] = re.sub('<[^<]+?>', '', str( stanforddf['Description'][i]))
    

stanforddf['Source'] = source
stanforddf['School'] = 'Stanford'


# In[6]:


html = urlopen(str('https://aai.haas.berkeley.edu/scheduling/CourseSchedule.aspx?Semester=Spring&Year=2019'))
soup = BeautifulSoup(html, 'html.parser')

results = soup.find_all('span')

titlelist = []

for result in results:
    if len(result.text) > 4:
    
        titlelist.append(result.text)
            
linklist = []

results = soup.find_all('a', class_='blue')

for result in results:
    try:
        linklist.append(result['href'])
    
    except:
        continue        
                
bigdictlist = []
errorlist = []

for i in range(len(linklist)):
    
    try:
        html = urlopen(linklist[i])
        soup = BeautifulSoup(html, 'html.parser')
        interimlist = []
        
        for j in soup.find_all('p'):
                
            interimlist.append(j.text)
            
        bigdict = {linklist[i]: interimlist}
        
        bigdictlist.append(bigdict)
        
    except:
        errorlist.append(i)
        print(i)
        
testlist = []
desclist = []

for i in bigdictlist:
    for j in i[str(tuple(i)[0])]:
        if "COURSE TITLE" in j:
            testlist.append(j)
            desclist.append(i)
    
#not complete yet. However the above code does work now. The point of this is to cross reference back to
#bigdictlist from the actual course title. 

coursetitlelist = []

for j in range(len(bigdictlist)):
    for i in testlist:
        if i in bigdictlist[j][str(tuple(bigdictlist[j])[0])]:
            
            coursetitlelist.append(j)
          

    #The numbers currently printing are the list indices from linklist which threw a 404 error when followed. Typing linklist[number] would give the link itself             


# In[7]:



haasdf = pd.DataFrame(testlist, columns= ['Course'])
haasdf['School'] = 'Haas'
haasdf['Source'] = ''
haasdf['Description'] = desclist
       
sourcelist = []

for i in range(len(desclist)):
    sourcelist.append(tuple(desclist[i])[0])
    
haasdf['Source']=sourcelist      

testlist = []

for i in range(len(haasdf)):

    testlist.append(haasdf['Description'][i][tuple(haasdf['Description'][i])[0]])

haasdf['Description'] = testlist    


# In[10]:


numlist = list(np.arange(1,23,1))

#The simplest and best so far.

source = 'https://michiganross.umich.edu/course-catalog'

html = urlopen(str(source))
soup = BeautifulSoup(html, 'html.parser')

linklist = []

linklist.extend(soup.find_all('a', class_="arrow small"))

for i in numlist:
    source = 'https://michiganross.umich.edu/course-catalog?page=' + str(i)
    html = urlopen(str(source))
    soup = BeautifulSoup(html, 'html.parser')
    
    linklist.extend(soup.find_all('a', class_="arrow small"))

desclist = []
courselist = []
sourcelist = []

#The better written the website, the more elegant the code to scrape it. 

for i in linklist:
    source = "https://michiganross.umich.edu" + str(i)[29:-16]
    html = urlopen(str(source))
    soup = BeautifulSoup(html, 'html.parser')

    desclist.extend(soup.find_all(attrs={'name':'description'}))
    courselist.append(str(soup.find_all(attrs={'name':'description'})).split(" ---",1)[0][16:] )
    sourcelist.append(source)
    
rossdf = pd.DataFrame(courselist, columns = ['Course'])

desc2list = []
for i in desclist:
    desc2list.append(str(i)[14:])

rossdf['Description'] = desc2list
rossdf['School'] = 'University of Michigan Ross'
rossdf['Source'] = sourcelist


# In[11]:


fulldf = pd.concat([hbsdf, whartondf, stanforddf, haasdf, rossdf], sort=True)
#partialdf = pd.concat([hbsdf, whartondf, stanforddf], sort=True)

#partialdict = partialdf.to_dict(orient='list')
fulldict = fulldf.to_dict(orient='list')


# In[12]:


#db.curriculum.insert_one(partialdict)
db.curriculum.insert_one(fulldict)


#Note: full database should appear in mongoDB. Format for the 'Description' field is not consistent, but this is due to the underlying HTML of the pages and
#would be more trouble than it was worth to standardize. 

#Especially for Haas, this field will give a dictionary with the key being the URL and the values being the content.
#This is because each description is a different URL, but some of these URLs led to 404 errors. 
#HBS has a similar structure, but it was possible to take only content in the "Description" field.


# In[ ]:



#Note: Remaining code is unfinished and has been commented out. 

#source='http://www.tuck.dartmouth.edu/mba/academic-experience/elective-curriculum/elective-courses'

#html = urlopen(str(source))
#soup = BeautifulSoup(html, 'html.parser')

#divlist = []
#for i in soup.find_all("div", class_='row content' ):
 #   i.contents.p


# In[ ]:


#divlist


# In[ ]:


#soup.find_all('div',class_='row content')


# In[ ]:


#This will have to wait until I have a more finished product to test on. 

#import pdfkit

#pdfkit.from_string(hbsdf, 'out.pdf')


# In[ ]:


#In class, making notes for later. Can use .strip to remove whitespace. 

#look for class or id when you are doing .find_all as an argument within the function.

