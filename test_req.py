from keras.models import load_model
from keras.applications.inception_v3 import preprocess_input
import numpy as np
from keras.preprocessing import image
from keras.preprocessing.sequence import pad_sequences
import json
from flask import Flask, render_template, Response, request
import tensorflow as tf
from tensorflow import keras
from flask import send_file
from ibm_watson import TextToSpeechV1
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os
from flask_cors import CORS

authenticator = IAMAuthenticator('ee-h6zbBluyPLbkW_FxyV2hpfpZ1mo1UM_sq9K8XQAxU')
text_to_speech = TextToSpeechV1(
    authenticator=authenticator
)


Lang_auth = IAMAuthenticator('czrVWPO9MNtdHFEO1o7lxxi-FjFyE9YRSI-c5Qr2_PiG')
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=Lang_auth
)

language_translator.set_service_url('https://api.eu-gb.language-translator.watson.cloud.ibm.com/instances/0bb973e5-fae9-4da7-9977-948bb697df55')



text_to_speech.set_service_url('https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/5ab89087-3fd4-404a-9551-2f2ab113e515')


os.environ['CUDA_VISIBLE_DEVICES'] = '-1'


model_new = tf.keras.models.load_model('models/inception')
max_length = 77
model = tf.keras.models.load_model('models/prediction.h5')

with open('json_data/wordtoix.json') as json_file: 
    wordtoix = json.load(json_file) 

with open('json_data/ixtoword.json') as json_file:
    ixtoword = json.load(json_file) 


def preprocess(image_path):
    # Convert all the images to size 299x299 as expected by the inception v3 model
    img = image.load_img(image_path, target_size=(299, 299))
    # Convert PIL image to numpy array of 3-dimensions
    x = image.img_to_array(img)
    # Add one more dimension
    x = np.expand_dims(x, axis=0)
    # preprocess the images using preprocess_input() from inception module
    x = preprocess_input(x)
    return x


def encode(image):
    image = preprocess(image) # preprocess the image
    fea_vec = model_new.predict(image) # Get the encoding vector for the image
    fea_vec = np.reshape(fea_vec, fea_vec.shape[1]) # reshape from (1, 2048) to (2048, )
    return fea_vec





def greedySearch(photo):
    in_text = 'startseq'
    for i in range(max_length):
        sequence = [wordtoix[w] for w in in_text.split() if w in wordtoix]
        sequence = pad_sequences([sequence], maxlen=max_length)
        yhat = model.predict([photo,sequence], verbose=0)
        yhat = np.argmax(yhat)
        word = ixtoword[str(yhat)]
        in_text += ' ' + word
        if word == 'endseq':
            break
    final = in_text.split()
    final = final[1:-1]
    final = ' '.join(final)
    return final

def get_lang(text, lang):
    lang = lang[0:2]
    lang = 'en-'+lang
    translation = language_translator.translate(
    text=text,
    model_id=lang).get_result()
    text = translation['translations'][0]['translation']
    return text
    


aa = {}
app = Flask(__name__)
CORS(app)
@app.route('/test', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        
        req_lang = request.form['lang']
        file = request.files['uploadfile'].read()

        f = open("get.jpg", "wb")

        f.write(file)
        f.close()

        encoding_train = {}

        encoding_train['get.jpg'] = encode('get.jpg')
        image = encoding_train['get.jpg'].reshape((1,2048))

        data_to_send = greedySearch(image)

        data_to_send = data_to_send[:len(data_to_send)-2]


        text = get_lang(data_to_send, request.form['lang'] )

        

        with open('hello_world.wav', 'wb') as audio_file:
            audio_file.write(
                text_to_speech.synthesize(
                    text,
                    voice=req_lang,
                    accept='audio/wav'        
                ).get_result().content)

        return send_file(
         'hello_world.wav', 
         mimetype="audio/wav", 
         as_attachment=True, 
         attachment_filename="test.wav")
        
        
@app.route('/')
def asd():
    return "Failure"


app.run('0.0.0.0',debug=True)