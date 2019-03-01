# WSGI script providing simple web GUI for Warden archive

# Configuration
PREFIX = "/data/warden_archive"
STATS_DIR = PREFIX + '/stats'
DAYS = 14

import flask
from flask import Flask, render_template
import os
from datetime import date, timedelta

application = app = Flask(__name__)

@app.route('/')
def main():
    data = [] # array of (date, cnt, cnt_test)
    
    # Load data from last DAYS days
    today = date.today()
    for i in range(1, DAYS+1):
        d = today - timedelta(days=i)
        d_str = d.isoformat()
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
    
    return render_template('main.html', data=data)

