import os
from flask import Flask

app = Flask("Moodio", static_folder="assets", static_url_path="/assets")
app.secret_key = os.urandom(32)

app.config["SPOTIFY_CLIENT_ID"] = "980bcda460d34f7bbdbf2fdce667c404"
app.config["SPOTIFY_CLIENT_SECRET"] = "7bdf7b1439ca42fb8e1dec0f65b135f3" # Not visible to the user
app.config["REDIRECT_URI"] = "http://localhost:5000/login/callback"

from app import auth, views