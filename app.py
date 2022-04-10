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


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/likability', methods=["POST"])
def predict():
    data = pd.DataFrame()
    try:
        url = request.args.get('search')
        if url is None:
            return render_template("index.html")
        if "https://open.spotify.com/playlist/" in url:
            playlist_id = url.replace("https://open.spotify.com/playlist/", "")
            data = spot.get_playlist_metadata(playlist_id)
        elif "https://open.spotify.com/track/" in url:
            track_id = url.replace("https://open.spotify.com/track/", "")
            data = spot.get_track_metadata(track_id)

        if len(data) > 0:
            data['value'] = model.predict(data.drop(columns=['label']))
            print(data)
            return render_template("output.html", data=data[['value', 'label']].to_dict())
        return render_template("error.html", error_message="No tracks found!")
    except ValueError:
        return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # app.run(port=port, host="0.0.0.0")
    app.run()
