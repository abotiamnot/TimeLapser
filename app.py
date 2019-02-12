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

# @app.before_request
# def before_request():
#     if 'login' in session:
#         pass
#     else:
#         return redirect(url_for('login'))

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
                 print("Stuck here broskis")
                 yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                 frame = camera.get_frame()
             print("Out here broskis")
             frame_file = open('/home/{date:%Y-%m-%d %H%M%S}.jpg'.format(date=datetime.now()), 'wb')
             frame_file.write(frame)
             frame_file.close()
         else:
             yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/thisshallneverwork')
# def gen(camera):
#     while True:
#          frame = camera.get_frame()
#          yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
    # wifi_ap_array = scan_wifi_networks()
    # config_hash = config_file_hash()
    global timelapse
    global record
    if request.method == 'POST':
        timelapse = int(request.form['inputTimeLapse'])
        record = True
    return render_template('timelapser.html')
    # return render_template('timelapser.html', wifi_ap_array = wifi_ap_array, config_hash = config_hash)

# @app.route('/securitycamera')
# def securitycamera():
#     return render_template('securitycamera.html')

@app.route('/visualizer')
def visualizer():
    return render_template('visualizer.html')

@app.route('/securitycamera')
def securitycamera():
    return render_template('securitycamera.html')

# The basics

#
# @app.route('/manual_ssid_entry')
# def manual_ssid_entry():
#     return render_template('manual_ssid_entry.html')
#
#
# @app.route('/wpa_settings')
# def wpa_settings():
#     config_hash = config_file_hash()
#     return render_template('wpa_settings.html', wpa_enabled=config_hash['wpa_enabled'], wpa_key=config_hash['wpa_key'])
#
#
#
# @app.route('/save_credentials', methods=['GET', 'POST'])
# def save_credentials():
#     ssid = request.form['ssid']
#     wifi_key = request.form['wifi_key']
#
#     create_wpa_supplicant(ssid, wifi_key)
#
#     # Call set_ap_client_mode() in a thread otherwise the reboot will prevent
#     # the response from getting to the browser
#     def sleep_and_start_ap():
#         time.sleep(2)
#         set_ap_client_mode()
#
#     t = Thread(target=sleep_and_start_ap)
#     t.start()
#
#     return render_template('save_credentials.html', ssid=ssid)
#
#
# @app.route('/save_wpa_credentials', methods=['GET', 'POST'])
# def save_wpa_credentials():
#     config_hash = config_file_hash()
#     wpa_enabled = request.form.get('wpa_enabled')
#     wpa_key = request.form['wpa_key']
#
#     if str(wpa_enabled) == '1':
#         update_wpa(1, wpa_key)
#     else:
#         update_wpa(0, wpa_key)
#
#     def sleep_and_reboot_for_wpa():
#         time.sleep(2)
#         os.system('reboot')
#
#     t = Thread(target=sleep_and_reboot_for_wpa)
#     t.start()
#
#     config_hash = config_file_hash()
#     return render_template('save_wpa_credentials.html', wpa_enabled=config_hash['wpa_enabled'],
#                            wpa_key=config_hash['wpa_key'])
#
#
# ######## FUNCTIONS ##########
#
# def scan_wifi_networks():
#     iwlist_raw = subprocess.Popen(['iwlist', 'scan'], stdout=subprocess.PIPE)
#     ap_list, err = iwlist_raw.communicate()
#     ap_array = []
#
#     for line in ap_list.decode('utf-8').rsplit('\n'):
#         if 'ESSID' in line:
#             ap_ssid = line[27:-1]
#             if ap_ssid != '':
#                 ap_array.append(ap_ssid)
#
#     return ap_array
#
#
# def create_wpa_supplicant(ssid, wifi_key):
#     temp_conf_file = open('wpa_supplicant.conf.tmp', 'w')
#
#     temp_conf_file.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n')
#     temp_conf_file.write('update_config=1\n')
#     temp_conf_file.write('\n')
#     temp_conf_file.write('network={\n')
#     temp_conf_file.write('	ssid="' + ssid + '"\n')
#
#     if wifi_key == '':
#         temp_conf_file.write('	key_mgmt=NONE\n')
#     else:
#         temp_conf_file.write('	psk="' + wifi_key + '"\n')
#
#     temp_conf_file.write('	}')
#
#     temp_conf_file.close
#
#     os.system('mv wpa_supplicant.conf.tmp /etc/wpa_supplicant/wpa_supplicant.conf')
#
#
# def set_ap_client_mode():
#     os.system('rm -f /etc/raspiwifi/host_mode')
#     os.system('rm /etc/cron.raspiwifi/aphost_bootstrapper')
#     os.system('cp /usr/lib/raspiwifi/reset_device/static_files/apclient_bootstrapper /etc/cron.raspiwifi/')
#     os.system('chmod +x /etc/cron.raspiwifi/apclient_bootstrapper')
#     os.system('mv /etc/dnsmasq.conf.original /etc/dnsmasq.conf')
#     os.system('mv /etc/dhcpcd.conf.original /etc/dhcpcd.conf')
#     os.system('reboot')
#
#
# def update_wpa(wpa_enabled, wpa_key):
#     with fileinput.FileInput('/etc/raspiwifi/raspiwifi.conf', inplace=True) as raspiwifi_conf:
#         for line in raspiwifi_conf:
#             if 'wpa_enabled=' in line:
#                 line_array = line.split('=')
#                 line_array[1] = wpa_enabled
#                 print(line_array[0] + '=' + str(line_array[1]))
#
#             if 'wpa_key=' in line:
#                 line_array = line.split('=')
#                 line_array[1] = wpa_key
#                 print(line_array[0] + '=' + line_array[1])
#
#             if 'wpa_enabled=' not in line and 'wpa_key=' not in line:
#                 print(line, end='')




if __name__ == '__main__':
    ip_ = find_local()
    print("Please connect to the following IP Address: {}".format(ip_))
    app.secret_key = os.urandom(24)
    # config_hash = config_file_hash()
    # if config_hash['ssl_enabled'] == "1":
    #     app.run(host='0.0.0.0', port=int(config_hash['server_port']), ssl_context='adhoc')
    # else:
    #     app.run(host='0.0.0.0', port=int(config_hash['server_port']))
    app.run(host='0.0.0.0',debug=True)
