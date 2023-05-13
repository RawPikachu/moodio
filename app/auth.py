from app import app
from flask import render_template, redirect, request, session, url_for
import requests

@app.route("/login")
def login():
    return redirect("https://accounts.spotify.com/authorize?client_id=" + app.config["SPOTIFY_CLIENT_ID"] + "&response_type=code&redirect_uri=" + app.config["REDIRECT_URI"] + "&scope=user-top-read user-follow-read")

@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    if code == None:
        return "Error: No code provided."
    else:
        session["code"] = code
        # Get access token
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": app.config["REDIRECT_URI"],
            "client_id": app.config["SPOTIFY_CLIENT_ID"],
            "client_secret": app.config["SPOTIFY_CLIENT_SECRET"]
        }
        r = requests.post("https://accounts.spotify.com/api/token", data=payload)
        if r.status_code == 200:
            session["access_token"] = r.json()["access_token"]
            session["refresh_token"] = r.json()["refresh_token"]
            return redirect(url_for("mood"))
        else:
            return "Error: " + str(r.status_code)
        