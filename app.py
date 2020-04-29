from flask import Flask, redirect, request, url_for, render_template, session
import secrets
import startup
import sys
import requests
import spotimine_api_handler as api
import spotimine_database_handler as database
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    response = startup.getUser()
    return redirect(response)

@app.route('/callback/')
def callback():
    cache = database.load_cache()
    startup.getUserToken(request.args['code'])

    # Check whether the setup process has been initialized/updated within 7 days
    if not database.check_tracks_updated(cache):

        # Initialize database and create tables
        database.create_database()
        database.drop_tables()
        database.create_tables()

        # Get access token used for making requests to spotify api
        authorization_header = startup.getAccessToken()[1] 

        # Get user track json after login
        user_tracks = api.get_user_tracks(authorization_header)

        # Prepare for write to db
        user_track_records = api.construct_sql_records(list_of_objs = user_tracks, kind = "track")

        # Write to db
        database.add_to_db(records = user_track_records, kind = "track") 

        # Get URIs for each track
        track_uri_list = api.get_uri_list(user_track_records)

        # Get audio features from API
        track_audio_features = api.get_track_audio_features(track_uri_list, authorization_header)

        # Prepare for write to db
        audio_feature_records = api.construct_sql_records(list_of_objs = track_audio_features, kind = "audio_feature")

        # Write to db
        database.add_to_db(records = audio_feature_records, kind = "audio_feature")

        # Finish setup by saving cache
        database.complete_setup(cache)
    
    return redirect(url_for("myspotimine"))

@app.route('/myspotimine')
def myspotimine():
    try:
        authorization_header = startup.getAccessToken()[1]
    except:
        return render_template("error.html")

    session["spotify_user_id"] = api.get_current_user_id(authorization = authorization_header)
    
    # Reset session keys for playlist after returning to myspotimine
    if "playlist_name" in session.keys():
        session.pop("playlist_name")

    if "generated_playlist" in session.keys():
        session.pop("generated_playlist")

    return render_template("myspotimine.html")

@app.route('/plot', methods = ['POST'])
def plot_graph():
    graph_criteria = request.form["graph_criteria"]
    graph = database.make_histogram(graph_criteria)
    return render_template(
        "generated_plot.html", 
        graph = graph, 
        graph_description = graph_criteria)

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    # Get playlist attributes from form
    playlist_name = request.form["playlistName"]
    tempo_value = request.form["tempoRange"]
    valence_value = request.form["valenceRange"]
    danceability_value = request.form["danceabilityRange"]
    energy_value = request.form["energyRange"]
    playlist_minutes = request.form["playlistMinutesRange"]

    # Get playlist restrictions from form
    ignore_tempo = "ignore_tempo" in request.form.keys()
    ignore_valence = "ignore_valence" in request.form.keys()
    ignore_energy = "ignore_energy" in request.form.keys()
    ignore_danceability = "ignore_danceability" in request.form.keys()

    # Create playlist from database
    database_playlist_records = database.make_playlist(
                                    tempo = tempo_value,
                                    valence = valence_value,
                                    danceability = danceability_value,
                                    energy = energy_value,
                                    duration_minutes = playlist_minutes,
                                    ignore_tempo = ignore_tempo,
                                    ignore_valence = ignore_valence,
                                    ignore_energy = ignore_energy,
                                    ignore_danceability = ignore_danceability
                                    )

    # Save playlist in session
    session["playlist_name"] = playlist_name
    session["generated_playlist"] = database_playlist_records

    return redirect(url_for("show_generated_playlist"))

@app.route('/generated')
def show_generated_playlist():
    # Redirect is used to prevent multiple form submission
    playlist = session["generated_playlist"]
    
    return render_template(
        "generated_playlist.html",
        playlist_name = session["playlist_name"],
        tracks = playlist
        )

@app.route('/import_to_spotify', methods = ['POST'])
def import_playlist_to_spotify():
    try:
        authorization_header = startup.getAccessToken()[1]
    except:
        return render_template("error.html")

    # Create empty playlist with submitted playlist name
    playlist_name = session["playlist_name"]
    new_playlist_id = api.create_empty_playlist(
        spotify_user_id = session["spotify_user_id"], 
        authorization = authorization_header, 
        playlist_name = playlist_name)

    # Fill created playlist with tracks
    playlist_tracks = session["generated_playlist"]
    playlist_tracks_to_send = ["spotify:track:" + track[1] for track in playlist_tracks] # prepend strings to format to api standard
    api.add_to_playlist(
        playlist_id = new_playlist_id,
        list_of_spotify_uris = playlist_tracks_to_send,
        authorization = authorization_header
    )

    # Get spotify link to created playlist
    web_link = api.get_web_player_link(new_playlist_id)

    return render_template("playlist_import_success.html", link = web_link)

if __name__ == "__main__":
    app.secret_key = secrets.session_secret
    app.run(debug=True)