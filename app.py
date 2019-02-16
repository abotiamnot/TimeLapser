from flask import Flask, render_template, redirect, url_for, session, request, Response, send_file
import os
import io
import pathlib
import zipfile
from importlib import import_module
from datetime import datetime
import time
from threading import Thread
import subprocess
import dynamic as dyn

Camera = import_module('camera_pi').Camera

app = Flask(__name__)

def find_local():
	return subprocess.check_output("hostname -I", shell=True).decode('utf-8').split(' ')[0]

@app.route('/')
def root():
    return redirect(url_for('login'))

record = False
timelapse = 0
current_name = None

@app.route('/thisshallneverwork', methods=['GET', 'POST'])
def gen(camera):
    global record
    global timelapse
    global current_name
    print(record)
    print(timelapse)
    while True:
         frame = camera.get_frame()
         if record is True:
             past = time.time()
             while time.time() - past < timelapse:
                 print(time.time() - past)
                 yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                 frame = camera.get_frame()
             print('/home/pi/photos/{}/{date:%Y-%m-%d %H%M%S}.jpg'.format(current_name, date=datetime.now()))
             frame_file = open('/home/pi/photos/{}/{date:%Y-%m-%d %H%M%S}.jpg'.format(current_name, date=datetime.now()), 'wb')
             frame_file.write(frame)
             print("Image Saved!")
             frame_file.close()
         else:
             yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/downloadable'):
# def directory():
#

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
    global current_name
    path = '/home/pi/photos/'
    if request.method == 'POST':
        if record == True:
            record = False
            zipper_()
            file_path = path + current_name + '.zip'
            return send_file(file_path,
                             mimetype='zip',
                             attachment_filename=current_name + '.zip',
                             as_attachment=True)
        else:
            current_name = '{date:%Y%m%d%H%M%S}'.format(date=datetime.now())
            pathlib.Path('/home/pi/photos/{}/'.format(current_name)).mkdir(parents=True, exist_ok=True)
            timelapse = int(request.form['inputTimeLapse'])
            record = True
    return render_template('timelapser.html', record_condition=record)

@app.route('/visualizer')
def visualizer():
    return render_template('visualizer.html')

@app.route('/securitycamera', methods=['GET', 'POST'])
def securitycamera():
    wifi_ap_array = scan_wifi_networks()
    if request.method == 'POST':
        try:
            if request.form['delete']:
              delete_request = int(request.form['delete'])
              del email_list[delete_request]
        except Exception:
               pass
        try:
           if request.form['email']:
              email_list.append(request.form['email_'])
        except Exception:
               pass
    return render_template('securitycamera.html', wifi_ap_array = wifi_ap_array, table=dyn.table_generate(email_list))


#############

@app.route('/manual_ssid_entry')
def manual_ssid_entry():
    return render_template('manual_ssid_entry.html')


@app.route('/save_credentials', methods = ['GET', 'POST'])
def save_credentials():
    ssid = request.form['ssid']
    wifi_key = request.form['wifi_key']
    create_wpa_supplicant(ssid, wifi_key)
    # Call set_ap_client_mode() in a thread otherwise the reboot will prevent
    # the response from getting to the browser
    def sleep_and_start_ap():
        time.sleep(2)
        set_ap_client_mode()
    t = Thread(target=sleep_and_start_ap)
    t.start()

    return render_template('save_credentials.html', ssid = ssid)




######## FUNCTIONS ##########

def scan_wifi_networks():
    iwlist_raw = subprocess.Popen(['iwlist', 'scan'], stdout=subprocess.PIPE)
    ap_list, err = iwlist_raw.communicate()
    ap_array = []

    for line in ap_list.decode('utf-8').rsplit('\n'):
        if 'ESSID' in line:
            ap_ssid = line[27:-1]
            if ap_ssid != '':
                ap_array.append(ap_ssid)

    return ap_array

def create_wpa_supplicant(ssid, wifi_key):
    temp_conf_file = open('wpa_supplicant.conf.tmp', 'w')

    temp_conf_file.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
    temp_conf_file.write('update_config=1\n')
    temp_conf_file.write('\n')
    temp_conf_file.write('network={\n')
    temp_conf_file.write('	ssid="' + ssid + '"\n')

    if wifi_key == '':
        temp_conf_file.write('	key_mgmt=NONE\n')
    else:
        temp_conf_file.write('	psk="' + wifi_key + '"\n')

    temp_conf_file.write('	}')

    temp_conf_file.close

    os.system('mv wpa_supplicant.conf.tmp /etc/wpa_supplicant/wpa_supplicant.conf')

def set_ap_client_mode():
    os.system('rm -f /etc/raspiwifi/host_mode')
    os.system('rm /etc/cron.raspiwifi/aphost_bootstrapper')
    os.system('cp /usr/lib/raspiwifi/reset_device/static_files/apclient_bootstrapper /etc/cron.raspiwifi/')
    os.system('chmod +x /etc/cron.raspiwifi/apclient_bootstrapper')
    os.system('mv /etc/dnsmasq.conf.original /etc/dnsmasq.conf')
    os.system('mv /etc/dhcpcd.conf.original /etc/dhcpcd.conf')
    os.system('cp /usr/lib/raspiwifi/reset_device/static_files/isc-dhcp-server.apclient /etc/default/isc-dhcp-server')
    os.system('reboot')

def config_file_hash():
    config_file = open('/etc/raspiwifi/raspiwifi.conf')
    config_hash = {}

    for line in config_file:
        line_key = line.split("=")[0]
        line_value = line.split("=")[1].rstrip()
        config_hash[line_key] = line_value

    return config_hash


def zipper_():
    global current_name
    print("Inside Zipper!")
    path = '/home/pi/photos/'
    zf = zipfile.ZipFile(path + current_name + '.zip', "w")
    for dirname, subdirs, files in os.walk(path + current_name):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()
    # print("Returning this {}".format(path + current_name + '.zip'))
    # attachment_filename = path + current_name + '.zip'
    # return send_file(attachment_filename,
    #                  mimetype='zip',
    #                  attachment_filename=attachment_filename,
    #                  as_attachment=True)

def check_if_exist():
    files_ = os.listdir('/home/pi/photos/')
    zips = [file for file in files_ if file[-3:] == 'zip']


 ###################

if __name__ == '__main__':
    ip_ = find_local()
    print("Please connect to the following IP Address: {}".format(ip_))
    app.secret_key = os.urandom(24)
    config_hash = config_file_hash()
    email_list = dyn.email_extractor()

    if config_hash['ssl_enabled'] == "1":
        app.run(host='0.0.0.0', port=int(config_hash['server_port']), ssl_context='adhoc')
    else:
        app.run(host='0.0.0.0', port=int(config_hash['server_port']))
    # app.run(host='0.0.0.0',debug=True)
