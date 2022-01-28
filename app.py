from re import template
import flask
from flask_cors import CORS, cross_origin
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import pandas as pd
import numpy as np
import time
import os


app=flask.Flask(__name__,template_folder='template')
cors=CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

import moviepy.editor as mp
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import argparse

import speech_recognition as sr
import time
from trans import google_translator  
import os
import sys
from gtts import gTTS
import base64

def speech_to_text(filename,lang="ta-IN"):    
    r = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data,language = lang)
        translator = google_translator()  
        
        t2=text.split(' ')
        translate_text =""
        for i in range(0,len(t2),11):
            print(str(' '.join(t2[i:min(10+i,len(t2))])))
            print(i,10+i)
            t= translator.translate(str(' '.join(t2[i:min(10+i,len(t2))])), lang_src='ta', lang_tgt='hi')
            time.sleep(2)
            translate_text+=t
    return {"text":text,"translate":translate_text}


def video_to_audio(videofile,src_lang="ta-IN",dest_lang='hi'):
    clip = VideoFileClip(videofile)
    filename=str(videofile[0:-4]+".wav")
    clip.audio.write_audiofile(filename)
    new_clip = clip.without_audio()
    texts=speech_to_text(filename,src_lang)
    
    myobj = gTTS(text=texts["translate"], lang=dest_lang, slow=False)
    myobj.save(str(videofile[0:-4]+"-converted"+".wav"))
    audio_background = AudioFileClip(str(videofile[0:-4]+"-converted"+".wav"))
    final = new_clip.set_audio(audio_background)
    final.write_videofile(str(videofile[0:-4]+"-OUTPUT"+".mp4"))
    return str(videofile[0:-4]+"-OUTPUT"+".mp4")

#videofile=str(sys.argv[1])
#src_lang=str(sys.argv[2])
#dest_lang=str(sys.argv[3])


import json


@app.route('/upload')
def upload_file():
    return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        filename=video_to_audio(f.filename)
        with open(filename, "rb") as videoFile:
            import hashlib
            s = str(base64.b64encode(videoFile.read()))
            return json.dumps(s)

if __name__ == '__main__':
    app.debug = True
    app.run()
    #app.run(host="127.0.0.1", port=7575)