from flask import Flask, jsonify, request
import time
import threading
import re
import json
from Misc import url_strip, search_thing, search_entry, search_vals
import datetime

url_timestamp = {}
url_viewtime = {}
prev_url = ""
app = Flask(__name__)

def run_flask():
    app.app_context().push()
    fthread = threading.Thread(target=start_flask).start()

@app.route('/send_url', methods=['POST'])
def send_url():
    url = request.form["url"]
    ic = request.form["ic_link"]
    url = url_strip(url)

    parent_url = url

    global url_timestamp
    global url_viewtime
    global prev_url

    print(url)
    print(ic)

    if parent_url not in url_timestamp.keys():
        url_viewtime[parent_url] = 0

    time_spent = 0

    if prev_url != '':
        time_spent = int(time.time() - url_timestamp[prev_url])
        url_viewtime[prev_url] = url_viewtime[prev_url] + time_spent

    x = int(time.time())
    url_timestamp[parent_url] = x
    prev_url = parent_url

    tday = datetime.datetime.today()
    ttp = tday.timetuple()
    day = ttp[2]

    json_info = {}
    js_list = []

    try:
        with open("info.json", 'r') as f:
            info = json.load(f)
            json_info = info
            json_info = search_entry(info, 'sites', url, time_spent, ic)
            print(json_info)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'message': 'nope nope!'}), 200

    with open("info.json", 'w') as f:
        json.dump(json_info, f, indent=1)

    return jsonify({'message': 'success!'}), 200

@app.route('/quit_url', methods=['POST'])
def quit_url():
    resp_json = request.get_data()
    print("Url closed: " + resp_json.decode())
    return jsonify({'message': 'quit success!'}), 200

def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)