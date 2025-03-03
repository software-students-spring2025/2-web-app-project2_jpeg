from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv, dotenv_values
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import certifi
from flask_login import current_user, login_required
import flask_login
import flask
import certifi
import re
import datetime


load_dotenv()

app = Flask(__name__)
app.config['SESSION_PROTECTION'] = "strong"
app.secret_key = "user_creds_k3ys"

#login 
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#app configs
config = dotenv_values()
app.config["DEBUG"] = os.getenv("DEBUG", "False") == "True"

#mongodb client
client = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = client[os.getenv("MONGO_DBNAME")]
db_2 = client[os.getenv("MONGO_DBNAME_2")]
tv_shows_collection = db.tv_shows
all_shows_collection = db_2.all_shows
users = db.users

class User(flask_login.UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.username = user_doc["username"]
        self.password = user_doc["password"]
        #self.password = hashlib.sha256(user_doc["password"]).hexdigest()

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id


@login_manager.user_loader
def user_loader(user_id):
    user_doc = users.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        return
    
    return User(user_doc)


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')

    if not username:
        return
    
    user_doc = users.find_one({"username": username})

    if not user_doc: #user doesn't exist
        return None

    return User(user_doc)

@app.route("/home")
@login_required
def home():
    '''if "user" in session:
        return render_template("home.html", username=session["user"])'''
    
    if not current_user.is_authenticated:
        flash("Please log in to view your episodes.", "danger")
        return redirect(url_for("login"))
    
    user_episodes = db[current_user.id]
    ep_collection = user_episodes.find({}).sort("date", -1)
    return render_template("home.html", username=current_user.id, episodes=ep_collection)

@app.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        entered_pw = request.form.get('password')

        if not username or not entered_pw:
            flash("Username and password are required", "danger")
            return redirect(url_for("login"))
    
        user_doc = users.find_one({"username": username})
        #password = users.find({"username": username})

        if user_doc and (entered_pw == user_doc["password"]): #correct credentials
            user = User(user_doc)
            #user.username = username
            flask_login.login_user(user)
            session["user"] = user.id
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
            return render_template("login.html")
        
    return render_template("login.html")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = users.find_one({"username": username})
        if existing_user:
            flash("Username already exists", "danger")
            return redirect(url_for("signup")) #, "Username already exists", "danger"

        new_doc = db.users.insert_one({"username": username, "password": password})
        user_id = str(new_doc.inserted_id)
        return redirect(url_for("login")) #, message="Sign up successful! You can now log in."
    return render_template("signup.html")

#add entry page
@app.route("/add", methods=["GET", "POST"])
def add():
    #get data from HTML form
    if request.method == "POST":
        title = request.form.get("title")
        genre = request.form.get("genre")
        season = request.form.get("season")
        episode = request.form.get("episode") 
        rating = request.form.get("rating") 
        date = request.form.get("date")
        tags = request.form.get("tags").split(",")
        comment = request.form.get("comment") 

        new_episode = {
            "title": title,
            "genre": genre,
            "season": season,
            "episode": episode,
            "rating": int(rating or 0),
            "tags": [tag.strip() for tag in tags],
            "date": date,
            "comment": comment,
        }

        user_id = current_user.id
        user_collection = db[user_id]

        #insert data into user collection (may need to change, possibly inefficient for large num of users)
        user_collection.insert_one(new_episode)
        db.tv_shows.insert_one(new_episode)
        return redirect(url_for("success"))

    return render_template("add_show.html")


@app.route("/search", methods=["GET"])
def search():
   user_episodes = db[current_user.id]
   all_episodes = db.all_shows.find({}).sort("date", -1)
   query = request.args.get("query")
   if query:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        search_criteria = {
            "$or": [
                {"title": {"$regex": pattern}},
                {"genre": {"$regex": pattern}},
                {"tags": {"$regex": pattern}}
            ]
        }
        results = user_episodes.find(search_criteria)
        shows = [
            {
                "id": str(show["_id"]),
                "title": show["title"],
                "genre": show.get("genre", ""),
                "seasons": show.get("seasons", ""),
                "rating": show["rating"],
                "tags": show.get("tags", []),
                "date": show.get("date", "")
            }
            for show in results
        ]
        return render_template("results.html", all_episodes=shows)
   return render_template("results.html", all_episodes=[])

@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        # Get the show_id from the form
        show_id = request.form["show_id"]
        
        if show_id:
            try:
                db[current_user.id].delete_one({"_id": ObjectId(show_id)})
                return render_template("success.html", message="Episode deleted successfully!")
            except Exception as e:
                return render_template("success.html", message=f"Error deleting show: {e}")

    # If it's a GET request, display the list of shows
    shows = db[current_user.id].find()
    return render_template("delete.html", shows=shows)

@app.route("/edit/<post_id>", methods=["GET", "POST"])
def edit(post_id):
    """
    Route to edit an existing episode.
    """
    show = db[current_user.id].find_one({"_id": ObjectId(post_id)})

    if request.method == "POST":
        title = request.form.get("title")
        genre = request.form.get("genre")
        season = request.form.get("season")
        episode_num = request.form.get("episode")
        rating = request.form.get("rating")
        tags = request.form.get("tags").split(",")
        date = request.form.get("date")
        comment = request.form.get("comment")

        episode = f"S{season}E{episode_num}" if season and episode_num else ""

        updated_episode = {
            "title": title,
            "genre": genre,
            "episode": episode,
            "rating": int(rating or 0),
            "tags": [tag.strip() for tag in tags],
            "date": date,  
            "comment": comment,
        }

        db[current_user.id].update_one({"_id": ObjectId(post_id)}, {"$set": updated_episode})

        return redirect(url_for("success"))

    return render_template("edit_show.html", show=show)

@app.route("/settings")
def settings():
    user_doc = users.find_one({"_id": ObjectId(current_user.id)})    
    if user_doc:
        username = user_doc.get("username", "Unknown")
        password = user_doc.get("password", "Not available")
    else:
        username = "Unknown"
        password = "Not available"
    return render_template("settings.html", username=username, password=password)

@app.route("/success")
def success():
    return render_template("success.html", message="Episode added successfully!")

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template("logout.html")

# main driver function
if __name__ == '__main__':
    app.run(debug=True)
