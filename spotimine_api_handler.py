import requests
import json
import spotimine_database_handler as db

# CONSTANTS #
CACHE_FILE_NAME = 'cache.json'
CACHE_DICT = {}

# ENDPOINTS #
BASE_URL = "https://api.spotify.com/v1"
USER = "/me"
TRACKS = "/tracks"
PLAYLISTS = "/playlists"
AUDIO_FEATURES = "/audio-features"


def get_user_tracks(authorization):
    '''Calls the Spotify endpoint

    returns
    flattened_list : list
        a list of track items returned from the api
    '''
    params = {"limit":50}
    response = requests.get(BASE_URL + USER + TRACKS, headers = authorization, params = params).json()

    pages = get_all_pages(response, authorization)

    flattened_list = [item for sublist in pages for item in sublist]
    
    return flattened_list

def construct_records(list_of_tracks):
    '''
    '''
    records = []
    for track_obj in list_of_tracks:
        records.append((track_obj["track"]["name"],track_obj["track"]["popularity"],track_obj["track"]["id"]))
    
    return records
    
# db.add_tracks_to_db(construct_records(flattened_list[0:5]))

def get_all_pages(response_json, authorization):
    '''
    '''
    params = {"limit":50}
    content = []
    content.append(response_json["items"])
    while response_json["next"]:
        response_json = requests.get(response_json["next"], headers = authorization, params = params).json()
        # response_json = make_url_request_using_cache(response_json["next"], CACHE_DICT, headers = authorization, params = params) TODO FIX CACHING
        content.append(response_json["items"])
        

    return content

def make_url_request_using_cache(url, cache, params = {}, headers = {}):
    '''Makes a request to a webpage. If the url has not been visited before,
        stores the url in a cache. Otherwise accesses url from cache.
    
    Parameters
    ----------
    url: str
        the url to request from

    cache : dict
        a local cache to check for the url
    params : dict
        a dictionary of parameters to be submitted in the url request
    Returns
    -------
    cache : dict
        a json like dictionary of the content stored at the cache or the result of a request.
    '''

    unique_key = construct_unique_key(url,params)

    if url in cache.keys() or unique_key in cache.keys():
        print("Using cache")
        if bool(params):
            return cache[unique_key]
        else:
            return cache[url]
    else:
        print("Fetching")
        response = requests.get(url, params = params, headers = headers)
        if bool(params):
            cache[unique_key] = response.text
            save_cache(cache)
            return cache[unique_key]
        else:
            cache[url] = response.json()
            save_cache(cache)
            return cache[url]

def construct_unique_key(baseurl, params):
    '''Creates a unique key of a url and parameters
    
    Parameters
    ----------
    baseurl : str
        a url to be combined with the parameters

    params : dict
        a dictionary of parameters to be parsed and concatenated to the url to form a key
    
    Returns
    -------
    unique_key : str
        a unique key to be used in caching
    '''

    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector +  connector.join(param_strings)

    return unique_key

def load_cache():
    '''Tries to load a cache to read, if none is found one is created
    
    Parameters
    ----------
    none
    
    Returns
    -------
    cache : dict
        a dictionary containing the found cache
    '''

    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.load(cache_file_contents)
        cache_file.close()
    except:
        cache = {}

    return cache

def save_cache(cache):
    '''Saves the contents passed in to the local cache
    
    Parameters
    ----------
    cache : dict
        a cache to save to
    
    Returns
    -------
    none
    '''

    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()