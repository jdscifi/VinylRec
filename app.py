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
data = spot.get_playlist_metadata("4jlbTgG7gqClTD2MjpUDqI")
data.to_csv("datsssa____.csv")


def load_model():
    try:
        with open(json_path, 'r') as json_file:
            loaded_model_json = json_file.read()
        loaded_model = tf.keras.models.model_from_json(loaded_model_json, custom_objects={'KerasLayer': hub.KerasLayer})
        loaded_model.load_weights(h5_path)
        loaded_model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.001, momentum=0.5),
                             loss=tf.keras.losses.BinaryCrossentropy(), metrics=['accuracy'])
        return loaded_model
    except Exception:
        return False


def spotify_search_track():
    pass


def get_track_metadata(id):
    pass


# image_input = np.array(np.expand_dims(image_input, axis=0), 'float32') / 255
# return model.predict(image_input, verbose=0)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/likability', methods=["POST", "GET"])
def predict():
    data = pd.DataFrame()
    try:
        url = request.args.get('search')
        if "https://open.spotify.com/playlist/" in url:
            playlist_id = url.replace("https://open.spotify.com/playlist/", "")
            data = spot.get_playlist_metadata(playlist_id)
        elif "https://open.spotify.com/track/" in url:
            track_id = url.replace("https://open.spotify.com/track/", "")
            data = spot.get_track_metadata(track_id)
        model = load_model()
        if len(data) > 0:
            y_pred = model.predict(data)
            return render_template("output.html")
        return render_template("error.html", error_message="No tracks found!")
    except ValueError:
        return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # app.run(port=port, host="0.0.0.0")
    app.run()
