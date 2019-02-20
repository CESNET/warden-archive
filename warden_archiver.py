#!/bin/env python3
# Script to archive incoming Warden messages into daily files.
# Each file conteins one IDEA message per line, files are named by date the
# messages were received.
#
# The current file is named YYYY-MM-DD.current. When date changes, this file is
# renamed to YYYY-MM-DD and the new .current file is created.

import sys
import os
import argparse
import signal
import json
import time
import datetime
from warden_client import Client, Error, read_cfg

argparser = argparse.ArgumentParser(description="Warden archiver -- receieves messages from Warden and put them to files in given directory. Each file is named by current date and contains one IDEA message per line.")
argparser.add_argument('warden_config', help='File with Warden configuration')
argparser.add_argument('-d', '--archive-dir', help='Path to archive directory', default='./archive')

# Write all messages to ARCHIVE_DIR/current
DEST_FILE_NAME = 'current'

# Additional config, may contain 'poll_time' and 'filter' (it could be settable by arguments, but it's not currently needed)
config = {}

running_flag = True

def terminate_me(signum, frame):
    global running_flag
    running_flag = False

signals = {
    signal.SIGTERM: terminate_me,
    signal.SIGINT: terminate_me,
}

# Copied from warden_filer, simplified and modified to write into a file rather than directory
def receiver(config, wclient, archive_dir):
    poll_time = config.get("poll_time", 5)
    conf_filt = config.get("filter", {})
    filt = {}
    # Extract filter explicitly to be sure we have right param names for getEvents
    for s in ("cat", "nocat", "tag", "notag", "group", "nogroup"):
        filt[s] = conf_filt.get(s, None)

    last_date = None

    while running_flag:
        count_ok = count_err = 0
        
        # Name file after the current date
        date = datetime.date.today().strftime("%Y-%m-%d")
        dest_file = os.path.join(args.archive_dir, date+".current")
        
        # If the date has changed, rename the old file (last_date.current -> last_date)
        if date != last_date and last_date is not None:
            try:
                os.rename(os.path.join(args.archive_dir, last_date+".current"), os.path.join(args.archive_dir, last_date))
            except OSError as e:
                print("Error: Can't rename {}.current to {}: {}".format(last_date, last_date, str(e)), file=sys.stderr)
        last_date = date
        
        # Get new events from Warden server
        events = wclient.getEvents(**filt)

        if not events:
            time.sleep(poll_time)
            continue

        # Write the recevied messages to the file
        with open(dest_file, 'a') as f:
            for event in events:
                try:
                    data = json.dumps(event, check_circular=False)
                    f.write(data + "\n")
                    count_ok += 1
                except Exception as e:
                    Error(message="Error saving event", exc=sys.exc_info(), file=dest_file,
                          event_ids=[event.get("ID")]).log(wclient.logger)
                    count_err += 1

        wclient.logger.info("warden_archiver: received %d, errors %d" % (count_ok, count_err))

if __name__ == "__main__":
    # Parse arguments
    args = argparser.parse_args()
    
    # Create Warden client
    wclient = Client(**read_cfg(args.warden_config))
    
    wclient.logger.info("Warden archiver started")
    
    # Ensure the archive directory exists
    os.makedirs(args.archive_dir, exist_ok=True)
    
    # Setup signal handlers
    for (signum, handler) in signals.items():
        signal.signal(signum, handler)
    
    # Run receiver
    receiver(config, wclient, args.archive_dir)

    wclient.logger.info("Warden archiver stopped")
