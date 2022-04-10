import json
import os
import requests as rq
import datetime as dt
import pandas as pd
import ast

TOKEN_FILE = "token_info.json"


class Spotify():
    def __init__(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE) as tkfile:
                data = json.load(tkfile)
            if data['timestamp'] < dt.datetime.timestamp(dt.datetime.now()):
                if not self.get_token():
                    raise Exception("Unable to connect to Spotify!")
            else:
                self.token = data['access_token']
                self.timeout = data['timestamp']

    def get_token(self):
        SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
        SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
        if SPOTIFY_CLIENT_ID is None or SPOTIFY_CLIENT_SECRET is None:
            raise Exception("Environment variable not accessed")
        # print(SPOTIFY_CLIENT_ID,SPOTIFY_CLIENT_SECRET)
        request_body = {
            "grant_type": "client_credentials",
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        }
        r = rq.post("https://accounts.spotify.com/api/token", data=request_body)
        if r.status_code == 200:
            resp = r.json()
            self.timeout = resp['timestamp'] = dt.datetime.timestamp(dt.datetime.now()) + 3600
            with open(TOKEN_FILE, "w") as tkfile:
                tkfile.write(json.dumps(resp))
            self.token = resp['access_token']
            return True
        return False

    def get_track_metadata(self, track_id, flag=False):
        if self.timeout < dt.datetime.timestamp(dt.datetime.now()):
            if not self.get_token():
                raise Exception("Unable to connect to Spotify!")
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {self.token}"}
        label = ""
        if not flag:
            response = rq.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers)
            if response.status_code == 200:
                label = response.json()["name"]
        response = rq.get(f"https://api.spotify.com/v1/audio-features/{track_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if not flag:
                data['label'] = label
                data = data_prep(data)
            return data
        else:
            return "unable to get track info"

    def get_playlist_metadata(self, playlist_id):
        if self.timeout < dt.datetime.timestamp(dt.datetime.now()):
            if not self.get_token():
                raise Exception("Unable to connect to Spotify!")
        headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {self.token}"}
        response = rq.get(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers)
        # if response.status_code == 200:
        df = pd.DataFrame(response.json())
        processed_info = pd.json_normalize(df['items'].apply(only_dict).tolist()).add_prefix('items_')
        track_data = []
        for ind, row in processed_info.iterrows():
            temp = self.get_track_metadata(row["items_track.id"], True)
            temp['label'] = row["items_track.name"]
            track_data.append(temp)
        return data_prep(track_data)


def data_prep(data):
    final_params = ['acousticness', 'danceability', 'duration_ms', 'energy', 'instrumentalness', 'liveness',
                    'loudness', 'mode', 'speechiness', 'tempo', 'valence', 'key_0', 'key_1', 'key_2', 'key_3',
                    'key_4', 'key_5', 'key_6', 'key_7', 'key_8', 'key_9', 'key_10', 'key_11', 'time_signature_1.0',
                    'time_signature_3.0', 'time_signature_4.0', 'time_signature_5.0']
    initial_parameters = ["acousticness", "danceability", "duration_ms", "energy", "instrumentalness", "key",
                          "liveness", "loudness", "mode", "speechiness", "tempo", "time_signature", "valence"]

    if isinstance(data, dict):
        data[f"key_{data['key']}"] = 1
        del data["key"]
        data[f"time_signature_{float(data['time_signature'])}"] = 1
        del data["time_signature"]
        data = [data]
        data = pd.DataFrame(data)
    else:
        data = pd.DataFrame(data)
        print(data)
        data = pd.concat([data, pd.get_dummies(data['key'])], axis=1)
        data['time_signature'] = data['time_signature'].astype(float)
        data = pd.concat([data, pd.get_dummies(data['time_signature'])], axis=1)

    unwanted_keys = set(data.keys()) - set(initial_parameters)
    unwanted_keys.remove("label")
    data.drop(columns=list(unwanted_keys), inplace=True)

    for i in final_params:
        if i not in data.columns:
            data[i] = [0] * len(data)

    return data


def only_dict(d):
    try:
        evaluated_json = ast.literal_eval(
            str(d).replace("None", '\"None\"').replace("True", '\"True\"').replace("False", '\"False\"'))
        return evaluated_json
    except ValueError:
        corrected = "\'" + str(d).replace("None", '\"None\"').replace("True", '\"True\"').replace("False",
                                                                                                  '\"False\"') + "\'"
        evaluated_json = ast.literal_eval(corrected)
        return evaluated_json


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
