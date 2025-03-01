from flask import Flask, render_template, request, redirect, url_for, session
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv, dotenv_values
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
import certifi
import re


load_dotenv()

app = Flask(__name__)

config = dotenv_values()
app.config["DEBUG"] = os.getenv("DEBUG", "False") == "True"

# app.config.from_mapping(config)

client = pymongo.MongoClient(os.getenv("MONGO_URI"), tls=True,
    tlsCAFile=certifi.where())
db = client[os.getenv("MONGO_DBNAME")]
db_2 = client[os.getenv("MONGO_DBNAME_2")]
tv_shows_collection = db.tv_shows
all_shows_collection = db_2.all_shows

@app.route("/")
def home():
    episodes = db.tv_shows.find({}).sort("date", -1)
    return render_template("home.html", episodes=episodes)

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

        #episode = f"S{season}E{episode_num}" if season and episode_num else ""

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

        #insert data into user collection (may need to change, possibly inefficient for large num of users)
        db.tv_shows.insert_one(new_episode)
        return redirect(url_for("success"))

    return render_template("add_show.html")


@app.route("/search", methods=["GET"])
def search():
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
        results = all_shows_collection.find(search_criteria)
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
                tv_shows_collection.delete_one({"_id": ObjectId(show_id)})
                return render_template("success.html", message="Episode deleted successfully!")
            except Exception as e:
                return render_template("success.html", message=f"Error deleting show: {e}")

    # If it's a GET request, display the list of shows
    shows = tv_shows_collection.find()
    return render_template("delete.html", shows=shows)

@app.route("/edit/<post_id>", methods=["GET", "POST"])
def edit(post_id):
    """
    Route to edit an existing episode.
    """
    show = tv_shows_collection.find_one({"_id": ObjectId(post_id)})

    if request.method == "POST":
        title = request.form.get("title")
        genre = request.form.get("genre")
        season = request.form.get("season")
        episode_num = request.form.get("episode")
        rating = request.form.get("rating")
        tags = request.form.get("tags").split(",")
        comment = request.form.get("comment")

        episode = f"S{season}E{episode_num}" if season and episode_num else ""

        updated_episode = {
            "title": title,
            "genre": genre,
            "episode": episode,
            "rating": int(rating or 0),
            "tags": [tag.strip() for tag in tags],
            "date": datetime.datetime.utcnow(),  # Keep track of when the edit happened
            "comment": comment,
        }

        tv_shows_collection.update_one({"_id": ObjectId(post_id)}, {"$set": updated_episode})

        return redirect(url_for("success"))

    return render_template("edit_show.html", show=show)

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/success")
def success():
    return render_template("success.html", message="Episode added successfully!")

# main driver function
if __name__ == '__main__':
    app.run(debug=True)
