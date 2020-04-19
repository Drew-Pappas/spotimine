from flask import Flask, redirect, request
import startup
import sys
import requests
import spotimine_api_handler as api

app = Flask(__name__)

@app.route('/')
def index():
    response = startup.getUser()
    print(response)
    return redirect(response)

@app.route('/callback/')
def callback():
    startup.getUserToken(request.args['code'])
    print(startup.getAccessToken(), file = sys.stderr)
    authorization_header = startup.getAccessToken()[1] # Access token used for making requests to spotify api
    # response = requests.get(url = "https://api.spotify.com/v1/me/", headers = header)
    # print(response.json()["next"], file = sys.stderr)
    # print(response.json()["id"], file = sys.stderr)

    api.get_user_tracks(authorization_header)
    return "callback route"

if __name__ == "__main__":
    app.run(debug=True)