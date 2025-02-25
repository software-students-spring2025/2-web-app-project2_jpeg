from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

#mongoDB client
client = MongoClient('localhost', 27017)
db = client.flask_db
todos = db.todos

sample_request = {
    "title": "Scandal",
    "season": 1,
    "episode": 2,
    "rating": 5,
    "comments": "Such an exciting start to the show!"
}

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return redirect(url_for('add'))

#add entry page
@app.route('/add', methods=['GET', 'POST'])
def add():
    #get data from HTML form
    if request.method == 'POST':
        show = request.form.get("show")
        season = request.form.get("season")
        episode = request.form.get("episode") 
        rating = request.form.get("rating") 
        comment = request.form.get("comment") 

        #insert data into user collection (may need to change, possibly inefficient for large num of users)
        db['user-entries'].insert_one({
            'title': show,
            'season': int(season or 0),
            'episode': int(episode or 0),
            'rating': int(rating or 0),
            'comment': comment
        })

        return redirect(url_for('add'))

    return render_template('add_show.html')

# main driver function
if __name__ == '__main__':
    app.run(debug=True)
