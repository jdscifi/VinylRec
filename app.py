import json
import os
import tensorflow as tf
import numpy as np
import tensorflow_hub as hub
from flask import Flask, render_template, request,  flash, redirect, url_for
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')
app = Flask(__name__)

json_path = "models/final_model.json"
h5_path = "models/final_model.h5"


def load_model():
    try:
        with open(json_path, 'r') as json_file:
            loaded_model_json = json_file.read()
        loaded_model = tf.keras.models.model_from_json(loaded_model_json, custom_objects={'KerasLayer': hub.KerasLayer})
        loaded_model.load_weights(h5_path)
        loaded_model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.001, momentum=0.5), loss=tf.keras.losses.BinaryCrossentropy(), metrics=['accuracy'])
        return loaded_model
    except Exception:
        return False


def spotify_search_track():
    pass


def get_track_metadata(id):
    pass


def model_predict(file_name):
    global model
    image_input = tf.keras.utils.img_to_array(
        tf.keras.utils.load_img(file_name, grayscale=False, target_size=IMAGE_INPUT_SIZE))
    image_input = np.array(np.expand_dims(image_input, axis=0), 'float32') / 255
    return model.predict(image_input, verbose=0)


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/likability', methods=['POST'])
def predict():
    # score = np.argmax(model_predict(get_track_metadata(spotify_search_track())), axis=1)
    return render_template("output.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # app.run(port=port, host="0.0.0.0")
    app.run()
