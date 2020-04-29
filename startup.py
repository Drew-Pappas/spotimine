# CODE ADAPTED FROM
# https://github.com/vanortg/Flask-Spotify-Auth

from flask_spotify_auth import getAuth, refreshAuth, getToken
import secrets
#Add your client ID
CLIENT_ID = secrets.client_id

#ADD YOUR CLIENT SECRET FROM SPOTIFY
CLIENT_SECRET = secrets.client_secret

#Port and callback url can be changed or ledt to localhost:5000
PORT = "5000"
CALLBACK_URL = "http://127.0.0.1"

#Add needed scope from spotify user
SCOPE = "user-library-read playlist-modify-public"
#token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown 
TOKEN_DATA = []


def getUser():
    return getAuth(CLIENT_ID, "{}:{}/callback/".format(CALLBACK_URL, PORT), SCOPE)

def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET, "{}:{}/callback/".format(CALLBACK_URL, PORT))
 
def refreshToken(time):
    time.sleep(time)
    TOKEN_DATA = refreshAuth()

def getAccessToken():
    return TOKEN_DATA
