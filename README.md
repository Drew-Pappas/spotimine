# Welcome to Spotimine!

To use Spotimine, run the app.py file from the terminal to start the locally hosted server. Opening the local server from the command line provides a GUI Flask app that can be interacted with through the browser. The app will not be able to run without the client secret key. Currently there is no way to get access to Spotimine without these keys. After the app is running, signing into Spotify and giving Spotimine permissions will allow you to use Spotimine's interactive features.

## Features:

### Library Analytics
After the user has provided authentication credentials to Spotify to allow access to their library, the user can view histograms of their library’s traits like danceability, tempo, popularity, key, acousticness, and more.  The histograms are generated by selecting traits from a dropdown menu displayed within a Flask app. The histograms are created with Plotly.

### Playlist Generator
The user can generate playlists based off of 5 library traits: tempo, mood, energy, danceability, and duration. Of those 5 traits, tempo, mood, energy, and danceability can all have options to ignore them in creating the playlist. If all options are ignored, then the generator will create playlists of random songs for whatever duration is specified by the user. Additionally, users provide a name for their playlist. 

### Playlist Importing
After the user generates a playlist using the playlist generator, they will be taken to a view where they can see all of the song titles for the playlist generated. With the push of a button they can import that generated playlist directly to spotify. After importing, they can view the imported playlist directly on spotify.

## Packages required:

Flask

    Flask, redirect, request, url_for, render_template, session

Requests

    requests

Plotly

    plotly.graph_objs

Sqlite

    sqlite3