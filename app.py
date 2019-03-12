


from flask import Flask, render_template, request, url_for, redirect
import pymongo
from flask_bootstrap import Bootstrap


app = Flask(__name__)
Bootstrap(app)

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.curriculumDB
#db.curriculum.delete_many({})
curriculum_collection = db.curriculum


# import things
from flask_table import Table, Col

# Declare your table (in this case, the full curriculum table)
class ItemTable(Table):
    School = Col('School')
    Course = Col('Course')
    Description = Col('Description')
    Source = Col('Source')
    #Data = Col('Data')


# Get some objects
class Item(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

# Populate the table
items = db.curriculum.find({})
table = ItemTable(items, border=True)

# Populate the table
dataitems = db.curriculum.find({'Data':1})
datatable = ItemTable(dataitems, border=True)

@app.route('/')
def index():
    # Store the entire collection in a list. Note this doesn't do anything right now,
    #want to save for later. 
    #data = db.curriculum.find()
    #print(type(data))
    #fulldatalist = list(data)
    #newvar = db.curriculum.find({'Data': 1})
    #print(fulldatalist)

    # Return the template with the teams list passed in
    return render_template('index.html',table=table)

@app.route('/full', methods=['GET', 'POST'])
def full():
    if request.method == 'POST':
        return redirect(url_for('full'))

    items = db.curriculum.find({})
    table = ItemTable(items, border=True)

    #if request.method == 'GET':
     #   return redirect(url_for('full'))   

    return render_template('full.html', table=table)


@app.route('/data', methods=['GET', 'POST'])
def data():
    if request.method == 'POST':
        return redirect(url_for('data'))

    dataitems = db.curriculum.find({'Data':1})
    datatable = ItemTable(dataitems, border=True)

    #if request.method == 'GET':
     #   return redirect(url_for('data'))

    return render_template('data.html', datatable = datatable)     

@app.route('/hbs', methods=['GET', 'POST'])
def hbs():
    if request.method == 'POST':
        return redirect(url_for('hbs'))

    hbsitems = db.curriculum.find({'Data':1, 'School': "Harvard Business School"})
    hbstable = ItemTable(hbsitems, border=True)

    #if request.method == 'GET':
     #   return redirect(url_for('data'))

    return render_template('hbs.html', hbstable = hbstable)    

@app.route('/wharton', methods=['GET', 'POST'])
def wharton():
    if request.method == 'POST':
        return redirect(url_for('wharton'))

    wharitems = db.curriculum.find({'Data':1, 'School': "Wharton"})
    whartable = ItemTable(wharitems, border=True)

    #if request.method == 'GET':
     #   return redirect(url_for('data'))

    return render_template('wharton.html', whartable = whartable)

@app.route('/stanford', methods=['GET', 'POST'])
def stanford():
    if request.method == 'POST':
        return redirect(url_for('stanford'))

    stanitems = db.curriculum.find({'Data':1, 'School': "Stanford"})
    stantable = ItemTable(stanitems, border=True)

    #if request.method == 'GET':
     #   return redirect(url_for('data'))

    return render_template('stanford.html', stantable = stantable)

@app.route('/haas', methods=['GET', 'POST'])
def haas():
    if request.method == 'POST':
        return redirect(url_for('haas'))

    haasitems = db.curriculum.find({'Data':1, 'School': "Haas"})
    haastable = ItemTable(haasitems, border=True)

    #if request.method == 'GET':
     #   return redirect(url_for('data'))

    return render_template('haas.html', haastable = haastable)

@app.route('/ross', methods=['GET', 'POST'])
def ross():
    if request.method == 'POST':
        return redirect(url_for('ross'))

    rossitems = db.curriculum.find({'Data':1, 'School': "University of Michigan Ross"})
    rosstable = ItemTable(rossitems, border=True)

    #if request.method == 'GET':
     #   return redirect(url_for('data'))

    return render_template('ross.html', rosstable = rosstable)

@app.route('/sloan', methods=['GET', 'POST'])
def sloan():
    if request.method == 'POST':
        return redirect(url_for('sloan'))

    sloanitems = db.curriculum.find({'Data':1, 'School': "MIT Sloan"})
    sloantable = ItemTable(sloanitems, border=True)

    #if request.method == 'GET':
     #   return redirect(url_for('data'))

    return render_template('sloan.html', sloantable = sloantable)




if __name__ == "__main__":
    app.run(debug=True)

