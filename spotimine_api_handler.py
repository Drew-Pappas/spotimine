import requests
import json
import spotimine_database_handler as db

# CONSTANTS #
# CACHE_FILE_NAME = 'cache.json'
# CACHE_DICT = {}

# ENDPOINTS #
BASE_URL = "https://api.spotify.com/v1"
USER = "/me"
TRACKS = "/tracks"
PLAYLISTS = "/playlists"
AUDIO_FEATURES = "/audio-features"
USERS = "/users"

class Track:
    def __init__(
        self,
        name = None,
        popularity = None,
        spotify_id = None,
        json = None
        ):
        if json is not None:
            self.json = json
            self.name = json["track"]["name"]
            self.popularity = json["track"]["popularity"]
            self.spotify_id = json["track"]["id"]
        else:
            self.json = json
            self.name = name
            self.popularity = popularity
            self.spotify_id = spotify_id

    def sql_record(self):
        '''Creates a tuple of the instance's name, popularity, and spotify id
    
        Parameters
        ----------
        self : track instance
            the current track instance
        
        Returns
        -------
        record : tuple
            a tuple of the instance's name, popularity, and spotify id
        '''

        record = (
            self.name,
            self.popularity,
            self.spotify_id
        )
        return record

class AudioFeature:
    def __init__(
        self, 
        spotify_id = None,
        duration = None,
        key = None,
        mode = None,
        time_signature = None,
        acousticness = None,
        danceability = None,
        energy = None,
        instrumentalness = None,
        liveness = None,
        loudness = None,
        speechiness = None,
        valence = None,
        tempo = None,
        json = None
        ):

        if json is not None:
            self.json = json
            self.spotify_id = json["id"]
            self.duration = json["duration_ms"]
            self.key = json["key"]
            self.mode = json["mode"]
            self.time_signature = json["time_signature"]
            self.acousticness = json["acousticness"]
            self.danceability = json["danceability"]
            self.energy = json["energy"]
            self.instrumentalness = json["instrumentalness"]
            self.liveness = json["liveness"]
            self.loudness = json["loudness"]
            self.speechiness = json["speechiness"]
            self.valence = json["valence"]
            self.tempo = json["tempo"]
        else:
            self.uri = uri
            self.duration = duration
            self.key = key
            self.mode = mode
            self.time_signature = time_signature
            self.acousticness = acousticness
            self.danceability = danceability
            self.energy = energy
            self.instrumentalness = instrumentalness
            self.liveness = liveness
            self.loudness = loudness
            self.speechiness = speechiness
            self.valence = valence
            self.tempo = tempo
    
    def sql_record(self):
        '''Creates a tuple representing many properties from the object 
    
        Parameters
        ----------
        self : audiofeature instance
            the current audiofeature instance
        
        Returns
        -------
        record : tuple
            a tuple representing many properties from the object 
        '''

        record = (
            self.spotify_id,
            self.duration, 
            self.key,
            self.mode,
            self.time_signature,
            self.acousticness,
            self.danceability,
            self.energy,
            self.instrumentalness,
            self.liveness,
            self.loudness,
            self.speechiness,
            self.valence,
            self.tempo)
        return record

def get_user_tracks(authorization):
    '''Calls the Spotify API tracks endpoint and pulls all of a users liked tracks
    Parameters
    ----------
    authorization : dict
        a dictionary containing the access token required for Oauth2 transactions

    Returns
    -------
    flattened_list : list
        a list of track items returned from the api
    '''

    params = {"limit":50}
    response = requests.get(BASE_URL + USER + TRACKS, headers = authorization, params = params).json()

    pages = get_all_pages(response, authorization)

    flattened_list = [item for sublist in pages for item in sublist]
    return flattened_list

def get_track_audio_features(spotify_uri_list, authorization):
    '''Calls the Spotify API audio features endpoint and pulls all of the audio features for a list of tracks
    Parameters
    ----------
    spotify_uri_list : list
        a list of strings that reference spotify URIs

    authorization : dict
        a dictionary containing the access token required for Oauth2 transactions

    Returns
    -------
    audio_features_list : list
        a list of json formatted audio features pulled from the api
    '''

    # CODE REFERENCE https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
    chunk_size = 100
    split_list = [spotify_uri_list[i * chunk_size:(i + 1) * chunk_size] for i in range((len(spotify_uri_list) + chunk_size - 1) // chunk_size )]
    audio_features_list = []

    for chunk in split_list:
        uri_string = ",".join(chunk)
        params = {"ids":uri_string} 
        response = requests.get(BASE_URL + AUDIO_FEATURES, params = params, headers = authorization).json()["audio_features"]
        for track_audio_feature in response:
            audio_features_list.append(track_audio_feature)
    return audio_features_list

def construct_sql_records(list_of_objs, kind):
    '''Calls the Spotify API audio features endpoint and pulls all of the audio features for a list of tracks
    Parameters
    ----------
    list_of_objs : list
        a list of objects to be converted to sql formatted records

    kind : str
        the type of the object

    Returns
    -------
    records : list
        a list of tuples formatted to be imported to the database
    '''

    records = []
    for obj in list_of_objs:
        if kind == "track":
            obj_to_record = Track(json = obj)
            records.append(obj_to_record.sql_record())
        elif kind == "audio_feature":
            obj_to_record = AudioFeature(json = obj)
            records.append(obj_to_record.sql_record())
    return records

def get_all_pages(response_json, authorization):
    '''Crawls the Spotify API pagination using links from the initial api request
    Parameters
    ----------
    response_json : json dict
        a json like dictionary of the initial api request

    authorization : dict
        a dictionary containing the access token required for Oauth2 transactions

    Returns
    -------
    content : list
        a list of json responses found by drilling through the pagination
    '''

    params = {"limit":50}
    content = []
    content.append(response_json["items"])
    while response_json["next"]:
        response_json = requests.get(response_json["next"], headers = authorization, params = params).json()
        content.append(response_json["items"])
    return content

def get_uri_list(list_of_tuples):
    '''Gets the all of the spotify URIs from a list of SQL formatted records
    Parameters
    ----------
    list_of_tuples : list
        a list of tuples in the format Track name, Track Popularity, Track spotify ID

    Returns
    -------
    uri_list : list
        a list of all URI strings found in the list of tuples
    '''
    
    uri_list = []
    for item in list_of_tuples:
        uri_list.append(item[-1])
    return uri_list

def get_current_user_id(authorization):
    '''Calls the Spotify api to get the current user and their spotify id
    Parameters
    ----------
    authorization : dict
        a dictionary containing the access token required for Oauth2 transactions

    Returns
    -------
    user_id : str
        the currently authenticated user's spotify user id
    '''
    
    response = requests.get(BASE_URL + USER, headers = authorization).json()
    user_id = response["id"]
    return user_id

def create_empty_playlist(spotify_user_id, authorization, playlist_name):
    '''Creates an empty playlist on the current user's spotify account
    Parameters
    ----------
    spotify_user_id : str
        the currently authenticated user's spotify user id

    authorization : dict
        a dictionary containing the access token required for Oauth2 transactions

    playlist_name : str
        the name of the playlist to be created

    Returns
    -------
    created_playlist_id : str
        the spotify ID of the created playlist
    '''
    
    endpoint = BASE_URL + USERS + "/" + spotify_user_id + PLAYLISTS
    body_data = {"name" : playlist_name}
    response = requests.post(url = endpoint, headers = authorization, json = body_data ).json()
    created_playlist_id = response["id"]
    return created_playlist_id

def add_to_playlist(playlist_id, list_of_spotify_uris, authorization):
    '''Adds tracks to a user's Spotify playlist
    Parameters
    ----------
    playlist_id : str
        the spotify id of the playlist to add tracks to

    list_of_spotify_uris : list
        a list of spotify uris that reference tracks to be added

    authorization : dict
        a dictionary containing the access token required for Oauth2 transactions

    Returns
    -------
    none
    '''
    
    endpoint = BASE_URL + PLAYLISTS + "/" + playlist_id + TRACKS
    body_data = {"uris": list_of_spotify_uris}
    response = requests.post(
        url = endpoint,
        headers = authorization,
        json = body_data)

def get_web_player_link(spotify_playlist_id):
    '''Creates a clickable link that references a spotify playlist
    Parameters
    ----------
    spotify_playlist_id : str
        the id of the spotify playlist to find

    Returns
    -------
    link : str
        a link to the spotify playlist found
    '''
    
    link = "http://open.spotify.com/user/spotify/playlist/" + spotify_playlist_id
    return link
