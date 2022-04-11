import os

import pandas as pd
import tensorflow as tf
from spotify_tasks import Spotify
import tensorflow_hub as hub
from flask import Flask, render_template, request, flash, redirect, url_for

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')
app = Flask(__name__)

json_path = "models/final_model.json"
h5_path = "models/final_model.h5"

spot = Spotify()


def load_model():
    try:
        return tf.keras.models.load_model("models/final_model")
    except Exception as e:
        return None


model = load_model()


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template("index.html")


@app.route('/predict', methods=["POST", "GET"])
def predict():
    data = pd.DataFrame()
    try:
        # if request.method == "POST":
        # print(request.args)
        # else:
        # return redirect(url_for('home'))
        url = request.args.get('search')
        if url is None:
            return redirect(url_for("home"))
        if "com/playlist/" in url:
            playlist_id = url.split("/")[-1]
            data = spot.get_playlist_metadata(playlist_id)
        elif "com/track/" in url:
            track_id = url.split("/")[-1]
            data = spot.get_track_metadata(track_id)
        if len(data) > 0:
            # data.to_csv("data.csv", index=False)
            y_pred = model.predict(data[['acousticness', 'danceability', 'duration_ms', 'energy',
       'instrumentalness', 'liveness', 'loudness', 'mode', 'speechiness',
       'tempo', 'valence', 'key_0', 'key_1', 'key_2', 'key_3', 'key_4',
       'key_5', 'key_6', 'key_7', 'key_8', 'key_9', 'key_10', 'key_11',
       'time_signature_1.0', 'time_signature_3.0', 'time_signature_4.0',
       'time_signature_5.0']])
            data['level'] = data['size'] = y_pred * 100
            data['label'] = data['label'] + "\n" + data['size'].apply(lambda x: str(int(x))) + "% Love Score"
            return render_template("output.html", data=data[['level', 'size', 'label']].to_dict("records"))
        return redirect(url_for("home"))
    except ValueError as e:
        print(e)
        return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host="0.0.0.0")
    # app.run(port=9000)  # ssl_context='adhoc')
