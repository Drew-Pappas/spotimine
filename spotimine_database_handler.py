import sqlite3


def create_database():
    '''Creates a sqlite db if it does not exist
    
    Parameters
    ----------
    none

    Returns
    ----------
    none
    '''

    create_tracks = '''
    CREATE TABLE IF NOT EXISTS "Tracks" (
        "Id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        "Name" TEXT NOT NULL,
        "Popularity"  INTEGER NOT NULL,
        "SpotifyId" TEXT,
        FOREIGN KEY(SpotifyId) REFERENCES AudioFeatures(Id)
    );
    '''
    create_audio_features = '''
    CREATE TABLE IF NOT EXISTS "AudioFeatures" (
        "Id"        TEXT PRIMARY KEY UNIQUE,
        "DurationMS"        INTEGER NOT NULL,
        "Key"        INTEGER NOT NULL,
        "Mode"        INTEGER NOT NULL,
        "TimeSignature"        INTEGER NOT NULL,
        "Acousticness"        REAL NOT NULL,
        "Danceability"        REAL NOT NULL,
        "Energy"        REAL NOT NULL,
        "Instrumentalness"        REAL NOT NULL,
        "Liveness"        REAL NOT NULL,
        "Loudness"        REAL NOT NULL,
        "Speechiness"        REAL NOT NULL,
        "Valence"        REAL NOT NULL,
        "Tempo"        REAL NOT NULL
        
    );
    '''

    conn = sqlite3.connect("spotimine.sqlite")
    cur = conn.cursor()
    cur.execute(create_tracks)
    cur.execute(create_audio_features)
    conn.commit()
    conn.close()

def add_tracks_to_db(records):
    '''
    Parameters:

    records : list
        list of tuples containing records to be inserted

    '''

    conn = sqlite3.connect('spotimine.sqlite')
    cur = conn.cursor()
    cur.executemany("INSERT INTO Tracks (Name, Popularity, SpotifyId) VALUES(?,?,?)", records)
    conn.commit()
    conn.close()


