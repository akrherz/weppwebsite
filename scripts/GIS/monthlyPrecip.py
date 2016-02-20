"""
  Generate a monthly shapefile of precipitation data
"""
import psycopg2
import dbflib
import datetime
import shutil
import os
import sys
WEPP = psycopg2.connect(database='wepp', host='iemdb', user='nobody')
wcursor = WEPP.cursor()

if len(sys.argv) == 1:
    now = datetime.datetime.now() - datetime.timedelta(days=1)
    sts = now.replace(day=1)
    ets = (sts + datetime.timedelta(days=35)).replace(day=1)
else:
    sts = datetime.datetime(int(sys.argv[1]), 1, 1)
    ets = datetime.datetime(int(sys.argv[1]), 12, 31)

now = sts
ohrap = {}
wcursor.execute("SELECT hrap_i from hrap_utm ORDER by hrap_i ASC")
for row in wcursor:
    ohrap[row[0]] = {'rain': 0, 'hours': 0, 'mrain': 0}

hrapi = ohrap.keys()
hrapi.sort()

while now < ets:
    dbfname = "%s_rain" % (now.strftime("%Y%m"), )
    dbf = dbflib.create(dbfname)
    dbf.add_field("RAINFALL", dbflib.FTDouble, 8, 2)
    dbf.add_field("RAINHOUR", dbflib.FTDouble, 8, 2)
    dbf.add_field("RAINPEAK", dbflib.FTDouble, 8, 2)

    wcursor.execute("""select hrap_i, rainfall /25.4 as rain,
        peak_15min /25.4 * 4 as mrain, hr_cnt / 4.0 as hours from
        monthly_rainfall_%s  WHERE valid = '%s'
        ORDER by hrap_i ASC
        """ % (now.strftime("%Y"), now.strftime("%Y-%m-%d")))

    hrap = ohrap
    for row in wcursor:
        hrap[row[0]] = {'rain': row[1],
                        'hours': row[3], 'mrain': row[2]}

    for i in range(len(hrapi)):
        key = hrapi[i]
        dbf.write_record(i, (hrap[key]['rain'], hrap[key]['hours'],
                             hrap[key]['mrain']))

    del dbf
    outdir = "/mnt/idep/data/rainfall/shape/monthly/%s" % (now.year,)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    shutil.copy(dbfname+".dbf", outdir)
    os.unlink("%s.dbf" % (dbfname,))

    now += datetime.timedelta(days=31)
