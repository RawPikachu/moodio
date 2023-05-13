import requests
from app import app
from flask import render_template, redirect, request, session, url_for
import random

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mood", methods=["GET", "POST"])
def mood():
    if not ("access_token" in session):
        return "Not logged in."
    
    if request.method == "POST":
        if "playlist" in session:
            del session["playlist"]
        session["energy"] = float(request.form["energy"])
        return redirect(url_for("playlist"))

    if request.method == "GET":
        return render_template("mood.html")

@app.route("/info")
def info():
    return render_template("info.html")

@app.route("/playlist")
def playlist():
    if not ("access_token" in session):
        return "Not logged in."
    
    if not ("playlist" in session):
        # Get user's top and followed artists
        top_artists = []
        followed_artists = []
        ranges = ["short_term", "medium_term", "long_term"]

        for r in ranges:
            req = requests.get("https://api.spotify.com/v1/me/top/artists?limit=50&time_range=" + r, headers={"Authorization": "Bearer " + session["access_token"]})
            if req.status_code == 200:
                for artist in req.json()["items"]:
                    top_artists.append(artist["uri"])
            else:
                return "Top Artists Error: " + str(req.status_code)
            
        req = requests.get("https://api.spotify.com/v1/me/following?type=artist&limit=50", headers={"Authorization": "Bearer " + session["access_token"]})
        if req.status_code == 200:
            for artist in req.json()["artists"]["items"]:
                followed_artists.append(artist["uri"])
        else:
            return "Following artists Error: " + str(req.status_code)
        
        # Get user's top tracks from top and followed artists
        top_tracks = []
        artists = top_artists + list(set(followed_artists) - set(top_artists))

        for artist in artists:
            req = requests.get("https://api.spotify.com/v1/artists/" + artist.split(":")[2] + "/top-tracks?country=US", headers={"Authorization": "Bearer " + session["access_token"]})
            if req.status_code == 200:
                for track in req.json()["tracks"]:
                    top_tracks.append(track["id"])
            else:
                return "Top Tracks Error: " + str(req.status_code)
            
        # Create playlist that matches mood

        random.shuffle(top_tracks)

        playlist = []

        mood = session["energy"]
        
        for chunk in list(chunks(top_tracks, 100)):
            req = requests.get("https://api.spotify.com/v1/audio-features?ids=" + ",".join(chunk), headers={"Authorization": "Bearer " + session["access_token"]})
            if req.status_code == 200:
                for track in req.json()["audio_features"]:
                    if mood < 0.1:
                        if (track["valence"] >= 0 and track["valence"] <= mood + 0.15 and
                            track["energy"] <= mood * 10 and
                            track["danceability"] <= mood * 8):
                            playlist.append(track["uri"])
                    elif mood >= 0.1 and mood < 0.25:
                        if (track["valence"] >= mood - 0.075 and track["valence"] <= mood + 0.075 and
                            track["energy"] <= mood * 5 and
                            track["danceability"] <= mood * 4):
                            playlist.append(track["uri"])
                    elif mood >= 0.25 and mood < 0.5:
                        if (track["valence"] >= mood - 0.05 and track["valence"] <= mood + 0.05 and
                            track["energy"] <= mood * 1.75 and
                            track["danceability"] <= mood * 1.75):
                            playlist.append(track["uri"])
                    elif mood >= 0.5 and mood < 0.75:
                        if (track["valence"] >= mood - 0.075 and track["valence"] <= mood + 0.075 and
                            track["energy"] <= mood / 2 and
                            track["danceability"] <= mood / 2.5):
                            playlist.append(track["uri"])
                    elif mood >= 0.75 and mood < 0.9:
                        if (track["valence"] >= mood - 0.075 and track["valence"] <= mood + 0.075 and
                            track["energy"] <= mood / 1.75 and
                            track["danceability"] <= mood / 2):
                            playlist.append(track["uri"])
                    elif mood >= 0.9:
                        if (track["valence"] >= mood - 0.15 and track["valence"] <= 1 and
                            track["energy"] <= mood / 1.5 and
                            track["danceability"] <= mood / 1.75):
                            playlist.append(track["uri"])
            else:
                return "Audio Features Error: " + str(req.status_code)
            
        session["playlist"] = playlist

        return render_template("playlist.html", playlist=session["playlist"])

    
    