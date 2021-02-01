# WSGI script providing simple web GUI for Warden archive

# Configuration
PREFIX = "/data/warden_archive"
STATS_DIR = PREFIX + '/stats'
DAYS = 14

import flask
from flask import Flask, render_template, request
import os
from datetime import date, timedelta

application = app = Flask(__name__)

@app.route('/') # optional param: days=<int>
def main():
    data = [] # array of (date, cnt, cnt_test)

    n_days = request.args.get("days", default=DAYS, type=int)
    n_days = max(min(n_days, 1000), 1) # limit to interval [1,1000]

    # Load data from last DAYS days
    today = date.today()
    for i in range(1, n_days+1):
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
    
    return render_template('main.html', n_days=n_days, data=data)

