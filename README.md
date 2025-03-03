# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

The TV Show Tracker application provides users with a simple and intuitive platform to track the TV shows and episodes they have watched.

## User stories

1. As a user, I want to  rate individual episodes of shows so that I can keep track of what I have watched.
2. As a user, I want to add tag values like "To Watch" or "Watched" so that I can manage my watchlist.
3. As a user, I want to be able to search for shows/episodes so that I can quickly find what I'm looking for. 
4. As a user I want to view a list of all of my tracked episodes so that I can see my watching history. 
5. As a user I want to be able to see my most recently watched episodes so that I can continue watching from where I left off. 
6. As a user, I want to be able to edit my tracked shows so that I can keep them up to date. 
7. As a user, I want to be able to delete episodes that I no longer want to keep track of. 
8. As a user, I want to be able to leave personal notes on specific episodes so that I can remember my thoughts on them. 
9. As a user, I want to add custom tags to episodes so that I can categorize them based on my preferences. 
10. As a user, I want to be able to track the date on which I watched each episode. 
11. As a user, I want to be able to individually rank episodes on a scale from 1-5. 
12. As a user, I want to keep track of each episode's title. 
13. As a user, I want to keep track of each episode's season number. 
14. As a user, I want to keep track of each episode's episode number. 
15. As a user, I want to keep track of each episode's genre.
16. As a user, I want to be able to log in to the site so that I can access my tracked shows. 
17. As a user, I want to be able to log out of the site to keep my account secure. 
18. As a user, I want to be able to adjust my app settings to customize my experience. 
19. As a user, I want to sign up for an account so that I can track my watched episodes. 
20. As a user, I want to delete my account if I am no longer interested in using the app. 

## Steps necessary to run the software

### Prerequisites

Before setting up the app, ensure you have the following installed:\
- **Python 3.8+**
- **pip**
- **Virtual Environment (pipenv or venv)**
- **A MongoDB Atlas account**

### 1. Set up a MongoDB Atlas Database

Instead of using MongoDB locally, we use MongoDB Atlas, which is a cloud-based database service. To set up MongoDB Atlas,
1. Go to [MongoDB Atlas](https://www.mongodb.com/products/platform/atlas-database) and sign in or create an account.
2. Create a **new cluster**.
3. Under **Database Access**, add a database user and password. Save these credentials.
4. Under **Network Access**, allow access from you IP address (0.0.0.0/0 allos access from anywhere).
5. Get the **connection string** from **Database > Clusters > Drivers > Python**. It should look something like: `mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority`

### 2. Create a `.env` File

A `.env` file is used to store sensitive information, like database credentials. Open the `.env` file in a text editor and add: 
```
MONGO_DBNAME=tv_shows
MONGO_DBNAME_2=all_shows
MONGO_URI=mongodb+srv://<your-username>:<your-password>@cluster0.mongodb.net/?retryWrites=true&w=majority
```
Replace `<your-username>` and `<your-password>` with your actual values. 

### 3. Set Up a Virtual Environment

To isolate dependencies, create and activate a virtual environment.

**Using `pipenv`**: 
```
pip install pipenv
pipenv shell
```

**Using `venv`**: 
```
python3 -m venv .venv
source .venv/bin/activate  # On Mac
.venv\Scripts\activate.bat     # On Windows
```

### 4. Install Dependencies  

Install the reqired packages: 
```
pip install -r requirements.txt
```

### 5. Run the App

Set the environment variables from the command line: 
**On Mac**
```
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```
**On Windows**
```
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```
The app will be available at `http://127.0.0.1:5000`

If the command `flask` is not found, you can alternatively run the app with `python3 -m flask run --host=0.0.0.0 --port=5000`

## Task boards

[Team JPEG - Sprint 1](https://github.com/orgs/software-students-spring2025/projects/31/views/1)\
[Team JPEG - Sprint 2](https://github.com/orgs/software-students-spring2025/projects/119/views/2)