from flask import Flask, request, jsonify, render_template
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
import tensorflow as tf
import pickle
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load model and tokenizer
my_model = tf.keras.models.load_model(r"C:\Users\DELL\Desktop\ICGapp\best_model.h5")
max_length = 35
with open(r"C:\Users\DELL\Desktop\ICGapp\tokenizer.pickle", 'rb') as handle:
    tokenizer = pickle.load(handle)

def extract_features(image):
    model = VGG16()
    model = Model(inputs=model.inputs, outputs=model.layers[-2].output)
    image = img_to_array(image)
    image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
    image = preprocess_input(image)
    features = model.predict(image, verbose=0)
    return features

def idx_to_word(integer, tokenizer):
    for word, index in tokenizer.word_index.items():
        if index == integer:
            return word
    return None

def predict_caption(model, image, tokenizer, max_length):
    in_text = 'startseq'
    for i in range(max_length):
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        sequence = pad_sequences([sequence], max_length)
        yhat = model.predict([image, sequence], verbose=0)
        yhat = np.argmax(yhat)
        word = idx_to_word(yhat, tokenizer)
        if word is None:
            break
        in_text += " " + word
        if word == 'endseq':
            break
    return in_text
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')  # Serve your HTML page

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        image = Image.open(file)
        image = image.resize((224, 224))
        features = extract_features(image)
        caption = predict_caption(my_model, features, tokenizer, max_length)
        caption = caption.replace('startseq', '').replace('endseq', '').strip().upper()

        return jsonify({'transcript': caption})

    return jsonify({'error': 'Error processing file'}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
