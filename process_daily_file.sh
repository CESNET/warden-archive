#!/bin/bash
# Process a finished daily archive of Warden data (part of Warden archiver)
# 
# This contains a set of oprations that should be done at the end of each day,
# when the daily file is complete.
#
# Takes one parameter - path/name of the finished file, which should look like
# /path/YYYY-MM-DD

prefix=/data/warden_archive
archive_dir=$prefix/archive
stats_dir=$prefix/stats

date=$1
if [ -z "$date" ] || ! grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2}$" <<<"$date" >/dev/null
then
  echo "ERROR: date not given or wrong format" >&2
  exit 1
fi

echo "== Processing $date ==" >&2

if ! [ -f "$archive_dir/$date" ]
then
  if [ -f "$archive_dir/$date.gz" ]
  then
    echo "INFO: File already compressed. Uncompressing first ..." >&2
    gzip -d "$archive_dir/$date.gz"
    echo "INFO: Done, continuing with processing as normal." >&2
  else
    echo "ERROR: '$archive_dir/$date' not found." >&2
    exit 2
  fi
fi

mkdir -p $stats_dir

# Compute statistics about number of alerts
<"$archive_dir/$date" tee >(grep -E '"Category": *\[[^]]*"Test"' | wc -l > $stats_dir/cnt-test-$date) | wc -l >$stats_dir/cnt-all-$date

# Compute number of alerts per Node.Name combination
<"$archive_dir/$date" jq -r '[.Node[].Name]|reverse|join(",")' | sort | uniq -c | sort -rn > $stats_dir/cnt-by-node-$date

# Compute number of alerts per Category
<"$archive_dir/$date" jq -r '.Category|join(",")' | sort | uniq -c | sort -rn > $stats_dir/cnt-by-cat-$date


# At last, compress the file.
gzip $archive_dir/$date

