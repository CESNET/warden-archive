# Warden archive

Simple script to continuosly download all data from [Warden](https://warden.cesnet.cz/) and store them in daily archives.

It periodically downloads new messages from Warden and stores them to files
in given directory. Each file contains messages recevied on a particular day,
one message per line. The files are named by the date, `YYYY-DD-MM`, the file
of the current day (which is still being filled) is named `YYYY-DD-MM.current`
and is renamed as soon as new file is to be created (i.e. just after midnight).

If the attached cron script is used, each finished file is automatically
processed by process_daily_file.sh script. By default, this script counts
number of alerts received in the day and then compress the file using gzip.
Thereore, in such setting, the `archive` directory contains gzipped files named
`YYYY-DD-MM.gz` instead. You can add any other commads to the script for
further processing.

The `warden_archiver.py` script should run constantly. It is recommended to run
it via systemd using the attached unit file (assuming systemd-based system). 

**Note:** The example configuration and other auxiliary files assume the
archive is located at `/data/warden_archive/` and the archive should be run by
user `wardenarchiver`.

## Installation

1. Create a system user to run warden_archiver:
```
useradd --system --no-create-home wardenarchiver
```

2. Create directory, copy necessary files and set ownership:
```
mkdir -p /data/warden_archive/archive
cp warden_archiver.py warden_client.cfg /data/warden_archive/
chown -R wardenarchiver:all-users /data/warden_archive/
```

3. Install warden_client Python library:
```
wget https://homeproj.cesnet.cz/tar/warden/warden_client_3.0-beta2.tar.bz2
tar -xjf warden_client_3.0-beta2.tar.bz2
cp warden_client_3.0-beta2/warden_client.py /usr/lib/python3*/site-packages/
rm -rf warden_client_3.0-beta2 warden_client_3.0-beta2.tar.bz2

# (Or rather use the latest version from git repository, if possible)
```

5. Set up warden connection:
  - [Register](https://warden.cesnet.cz/en/participation) a new receiving Warden client on a Warden server.
  - Use the obtained password with the `warden_apply.sh` script:
```
cd /data/warden_archive/
wget https://homeproj.cesnet.cz/tar/warden/warden_apply.sh
chmod +x warden_apply.sh
sudo -u wardenarchiver ./warden_apply.sh PASSWORD
# PEM key and certificate gets created
```
  - Edit `/data/warden_archive/warden_client.cfg`:
    - Set URL of warden server
    - Set name of the client

6. (optional) Test that everything works:
```
sudo -u wardenarchiver python3 ./warden_archiver.py warden_client.cfg -d /data/warden_archive/archive
# stop by pressing Ctrl-C
```

7. Set `warden_archiver.py` to run automatically *(tested on CentOS 7, but should work on other systemd-based systems as well)*:
```
cp warden-archiver.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable warden-archiver-filer
systemctl start warden-archiver-filer
```
9. (optional) Set up cron to process and compress data periodically:
```
cp warden_archiver.cron /etc/cron.d/warden_archiver
```

10. (optional) Set up logrotate to rotate `warden_archiver.log`:
```
cp warden_archiver.logrotate /etc/logrotate.d/warden_archiver
```
