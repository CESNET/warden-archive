# WSGI script providing simple web GUI for Warden archive

# Configuration
PREFIX = "/data/warden_archive"
STATS_DIR = PREFIX + '/stats'
DAYS = 14

import flask
from flask import Flask, render_template, request
import os
from datetime import date, timedelta
import re

application = app = Flask(__name__)

def process_file(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            # Extract the number and the label using regular expressions
            match = re.match(r'\s*(\d+)\s+(.+)', line)
            if match:
                number = int(match.group(1))
                label = match.group(2)
                data.append([label, number])
    return data


@app.route('/', methods=['GET', 'POST']) # optional param: days=<int>
def main():
    cat_data = {} # dict of { "date" : [[label, data], ...], ... }
    data = [] # array of (date, cnt, cnt_test)

    n_days = request.args.get("days", default=DAYS, type=int)
    n_days = max(min(n_days, 1000), 1) # limit to interval [1,1000]

    # Load data from last DAYS days
    today = date.today()
    default_key = ""
    for i in range(1, n_days+1):
        d = today - timedelta(days=i)
        d_str = d.isoformat()
        try:
            filename = os.path.join(STATS_DIR, "cnt-by-cat-" + d_str)
            cat_data[d_str] = process_file(filename)
            if i == 1:
                default_key = d_str

        except Exception as e:
            print("Failed to read {}: {}".format(filename, str(e)))
	
        try:
            filename = os.path.join(STATS_DIR, "cnt-all-" + d_str)
            with open(filename, "r") as f:
                cnt = int(f.read(50)) # (there should by a single number, limit read to 50 chars, just for sure)
        except Exception as e:
            print("Failed to read {}: {}".format(filename, str(e)))
            cnt = None
        try:
            filename = os.path.join(STATS_DIR, "cnt-test-" + d_str)
            with open(filename, "r") as f:
                cnt_test = int(f.read(50))
        except Exception as e:
            print("Failed to read {}: {}".format(filename, str(e)))
            cnt_test = None
        data.append( (d_str, cnt, cnt_test) )

    # Updating key
    default_key = request.form.get('selected_key', default_key)   
     
    return render_template('main.html', n_days=n_days, data=data, cat_data=cat_data, selected_key=default_key)

