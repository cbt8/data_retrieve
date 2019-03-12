
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
import re
import pymongo
import numpy as np
import os


# In[2]:


conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.curriculumDB
db.curriculum.delete_many({})
curriculum_collection = db.curriculumDB


if os.path.exists("./MBA_data.xlsx"):
  os.remove("./MBA_data.xlsx")
else:
  print("Clean file will be produced.")


# In[3]:


#First is HBS

print('HBS')

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
    rawlist = []
    
    for j in descsoup.findAll('p'):
        rawlist.append(j.text)
        
    descraw.append(rawlist)
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
    hbsdf['Description'][i]= hbsdf['Description'][i]
    
    hbsdf['Source'][i] = 'https://www.hbs.edu/'+ linklist[i]

#This writes everything to a dataframe. Easy to export to excel. The original data is stored in a list, so it could
#easily be written to a different kind of object, but I have used dataframes here for convenience.


for i in range(len(hbsdf['Description'])):
    for j in range(len(hbsdf['Description'][i])):
        hbsdf['Description'][i][j] = hbsdf['Description'][i][j].replace('\n', '')


# In[4]:


#Next is Wharton. This was the first code that I wrote, so it is a bit clunkier. Also, this includes prerequisites. (Note: this is removed in current mongoDB version)
#I have decided to remove this from the final version, because it is outside the scope of the original project.

print('Wharton')

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

print('Stanford')

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
        
for i in range(len(titlelist)):
    titlelist[i] = re.sub('<[^<]+?>', '', str(titlelist[i]))     
        
try:
    stanforddf = pd.DataFrame(titlelist, columns=["Course"])

except:
    print('Stanford webpage changed (dataframe conversion)')
    
stanforddf['Description'] = desclist

for i in range(len(stanforddf)):
    stanforddf['Course'][i] = re.sub('<[^<]+?>', '', str( stanforddf['Course'][i]))
    stanforddf['Description'][i] = re.sub('<[^<]+?>', '', str( stanforddf['Description'][i]))
    stanforddf['Description'][i] = stanforddf['Description'][i].replace('\n', '')

stanforddf['Source'] = source
stanforddf['School'] = 'Stanford'


# In[6]:


print('Haas')

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
        print("The following index threw a 404 error: i=" + str(linklist[i]) + " Don't worry, this is expected.")
        
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

for i in range(len(haasdf['Description'])):
    for j in range(len(haasdf['Description'][i])):
        haasdf['Description'][i][j] = haasdf['Description'][i][j].replace('\n', ' ')
        haasdf['Description'][i][j] = haasdf['Description'][i][j].replace('\r\n', ' ')
        haasdf['Description'][i][j] = haasdf['Description'][i][j].replace('\r', ' ')
        haasdf['Description'][i][j] = haasdf['Description'][i][j].replace('\xa0', ' ')


# In[8]:


numlist = list(np.arange(1,23,1))

print('University of Michigan Ross')
print('(This one takes quite a while. Thanks for your patience)')
#The simplest and best so far.

source = 'https://michiganross.umich.edu/course-catalog'

html = urlopen(str(source))
soup = BeautifulSoup(html, 'html.parser')

rlinklist = []

rlinklist.extend(soup.find_all('a', class_="arrow small"))

for i in numlist:
    
    try:
    
        source = 'https://michiganross.umich.edu/course-catalog?page=' + str(i)
        html = urlopen(str(source))
        soup = BeautifulSoup(html, 'html.parser')
    
        rlinklist.extend(soup.find_all('a', class_="arrow small"))

    except:
        
        print(source)
        
desclist = []
courselist = []
sourcelist = []

#The better written the website, the more elegant the code to scrape it. 

for i in rlinklist:
    
    try:
    
        source = "https://michiganross.umich.edu" + str(i)[29:-16]
        html = urlopen(str(source))
        soup = BeautifulSoup(html, 'html.parser')

        desclist.extend(soup.find_all(attrs={'name':'description'}))
        courselist.append(str(soup.find_all(attrs={'name':'description'})).split(" ---",1)[0][16:] )
        sourcelist.append(source)
    
    except:
        print(source)
rossdf = pd.DataFrame(courselist, columns = ['Course'])

desc2list = []
for i in desclist:
    desc2list.append(str(i)[14:])

rossdf['Description'] = desc2list
rossdf['School'] = 'University of Michigan Ross'
rossdf['Source'] = sourcelist


# In[9]:


print('MIT Sloan')

source = "http://student.mit.edu/catalog/m15a.html"

html = urlopen(str(source))
soup = BeautifulSoup(html, 'html.parser')

courselist = []
desclist = []
sourcelist = []

for i in soup.find_all('h3'):
   # courselist.extend([re.sub('<[^<]+?>', '', str([i]))])
    courselist.append(i.text)
    sourcelist.append(source)
for i in soup.find_all('p'):    
    desclist.append(i.text)

source = "http://student.mit.edu/catalog/m15b.html"
        
html = urlopen(str(source))
soup = BeautifulSoup(html, 'html.parser')


for i in soup.find_all('h3'):
    #courselist.extend([re.sub('<[^<]+?>', '', str([i]))])
    courselist.append(i.text)
    sourcelist.append(source)
for i in soup.find_all('p'):    
    desclist.append(i.text)    

sloandf = pd.DataFrame(courselist, columns=['Course'])
#This next part is necessary because one class, 15.329, does not have a description.
sloandf['Description'] = ''

for i in range(len(courselist)):
    for j in range(len(desclist)):
        if str(courselist[i])[:6] == str(desclist[j])[:6]:
            
            sloandf['Description'][i] = desclist[j] 
            
sloandf['School'] = 'MIT Sloan'
sloandf['Source'] = sourcelist


for j in range(len(sloandf['Description'])):
        sloandf['Description'][j] = sloandf['Description'][j].replace('\n', ' ')


# In[10]:


fulldf = pd.concat([hbsdf, whartondf, stanforddf, haasdf, rossdf, sloandf], sort=True)
#partialdf = pd.concat([hbsdf, whartondf, stanforddf], sort=True)

fulldf.to_excel("./MBA_data.xlsx")

#partialdict = partialdf.to_dict(orient='list')
fulldict = fulldf.to_dict(orient='list')


# In[11]:


#db.curriculum.insert_one(partialdict)
db.curriculum.insert_one(fulldict)

print('Success! The database can be found at "mongodb://localhost:27017"')

#Note: full database should appear in mongoDB. Format for the 'Description' field is not consistent, but this is due to the underlying HTML of the pages and
#would be more trouble than it was worth to standardize. 

#Especially for Haas, this field will give a dictionary with the key being the URL and the values being the content.
#This is because each description is a different URL, but some of these URLs led to 404 errors. 
#HBS has a similar structure, but it was possible to take only content in the "Description" field.


# In[12]:



#Note: Remaining code is unfinished and has been commented out. 

#source='http://www.tuck.dartmouth.edu/mba/academic-experience/elective-curriculum/elective-courses'

#html = urlopen(str(source))
#soup = BeautifulSoup(html, 'html.parser')

#divlist = []
#for i in soup.find_all("div", class_='row content' ):
 #   i.contents.p


# In[13]:


#divlist


# In[14]:


#soup.find_all('div',class_='row content')


# In[15]:


#This will have to wait until I have a more finished product to test on. 

#import pdfkit

#pdfkit.from_string(hbsdf, 'out.pdf')


# In[16]:


#In class, making notes for later. Can use .strip to remove whitespace. 

#look for class or id when you are doing .find_all as an argument within the function.

