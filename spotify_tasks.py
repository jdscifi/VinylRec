import json
import os
import requests as rq
import datetime as dt


def spotify_setup():
    SPOTIFY_CLIENT_ID = '7742b2da6b2a4544b6e2b04a2e3c1738'
    SPOTIFY_CLIENT_SECRET = '3937110194404e52bac848fa7b932a0e'

    SPOTIFY_TOKEN = "https://accounts.spotify.com/api/token"
    request_body = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    r = rq.post(url=SPOTIFY_TOKEN, data=request_body)
    if r.status_code == 200:
        resp = r.json()
        resp['timestamp'] = dt.datetime.timestamp(dt.datetime.now()) + 3600
        with open("token_info.json", "w") as tkfile:
            tkfile.write(json.dumps(resp))
        return resp['access_token']
    return None


def get_token():
    if os.path.exists("token_info.json"):
        with open("token_info.json") as tkfile:
            data = json.load(tkfile)
        if data['timestamp'] < dt.datetime.timestamp(dt.datetime.now()):
            return spotify_setup()
        else:
            return data['access_token']


"""def search_track(query_string=""):
    headers = {
        'Content-Type': 'application/json',
    }

    params = {
        "query": "track:{}".format(urllib3.request.urlencode(query_string)),
        'type': 'track',
        'include_external': 'audio',
    }

    response = rq.get(\'https://api.spotify.com/v1/search\', headers=headers, params=params)
    if response.status_code == 200:
        return"""


"""
https://open.spotify.com/track/59hSaWp9MXxrpYTUHNEKNj
"""


def get_track_metadata(track_id):
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {get_token()}"
    }
    response = rq.get(f"https://api.spotify.com/v1/audio-features/{track_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return "unable to get track info"


def get_playlist_metadata(playlist_id):
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Bearer {get_token()}"
    }
    response = rq.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)
    if response.status_code == 200:
        return response.json()

