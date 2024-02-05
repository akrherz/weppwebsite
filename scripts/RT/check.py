import os

import iemdb
import mx.DateTime

WEPP = iemdb.connect("wepp")
wcursor = WEPP.cursor()

os.chdir("/mnt/idep/RT")
sts = mx.DateTime.DateTime(2013, 1, 1)
ets = mx.DateTime.DateTime(2014, 1, 20)
interval = mx.DateTime.RelativeDateTime(days=1)
now = sts

while now < ets:
    wcursor.execute(
        """SELECT count(*) from results_by_twp where
  valid = '%s'"""
        % (now.strftime("%Y-%m-%d"),)
    )
    row = wcursor.fetchone()
    if row[0] != 1579:
        print(now, row)
        os.system(
            "python /opt/weppwebsite/scripts/RT/processEvents.py %s"
            % (now.strftime("%Y %m %d"),)
        )
        os.system("psql -h iemdb -f insert.sql wepp")
        os.system(
            "python /mesonet/www/apps/weppwebsite/scripts/RT/summarize.py %s"
            % (now.strftime("%Y %m %d"),)
        )
    now += interval
