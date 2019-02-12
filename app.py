from flask import Flask, render_template, redirect, url_for, session, request, Response
import os
from importlib import import_module
from datetime import datetime
import time
from threading import Thread
import subprocess
import fileinput

Camera = import_module('camera_pi').Camera

app = Flask(__name__)

def find_local():
	return subprocess.check_output("hostname -I", shell=True).decode('utf-8').split(' ')[0]

@app.route('/')
def root():
    return redirect(url_for('login'))

record = False
timelapse = 0

@app.route('/thisshallneverwork', methods=['GET', 'POST'])
def gen(camera):
    global record
    global timelapse
    print(record)
    print(timelapse)
    while True:
         frame = camera.get_frame()
         if record is True:
             past = time.time()
             while(time.time() - past < timelapse):
                 yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                 frame = camera.get_frame()
             frame_file = open('/home/{date:%Y-%m-%d %H%M%S}.jpg'.format(date=datetime.now()), 'wb')
             frame_file.write(frame)
             frame_file.close()
         else:
             yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form['pass'] == 'admin' and request.form['user'] == 'admin':
            session['login'] = True
            return redirect(url_for('main_menu'))
    return render_template('login.html')

@app.route('/menu')
def main_menu():
    return render_template('menu.html')

@app.route('/timelapser', methods=['GET', 'POST'])
def timelapser():
    global timelapse
    global record
    if request.method == 'POST':
        timelapse = int(request.form['inputTimeLapse'])
        record = True
    return render_template('timelapser.html')

@app.route('/visualizer')
def visualizer():
    return render_template('visualizer.html')

@app.route('/securitycamera')
def securitycamera():
    return render_template('securitycamera.html')


if __name__ == '__main__':
    ip_ = find_local()
    print("Please connect to the following IP Address: {}".format(ip_))
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0',debug=True)
