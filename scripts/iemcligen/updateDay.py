
import network
nt = network.Table(("IA_ASOS", "AWOS"))
import datetime
import sys
import psycopg2

WEPP = psycopg2.connect(database='wepp', host='iemdb')
wcursor = WEPP.cursor()
IEM = psycopg2.connect(database='iem', host='iemdb')
icursor = IEM.cursor()
ASOS = psycopg2.connect(database='asos', host='iemdb')
acursor = ASOS.cursor()

ts = datetime.datetime.now() - datetime.timedelta(days=1)
if len(sys.argv) == 4:
    ts = datetime.datetime( int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
day = ts.strftime("%Y-%m-%d")


targets = {'SUX': 1, 'MCW': 2, 'DBQ': 3, 
        'DNS': 4, 'DSM': 5, 'CID': 6,
        'ICL': 7, 'LWD': 8, 'BRL': 9}

# Lets find average wind speed, dew point for station
sql = """SELECT avg(sknt) * 2 as wvl from t%s WHERE sknt >= 0 and 
       date(valid) = '%s'""" % (ts.year, day)
acursor.execute( sql )
row = acursor.fetchone()

wvl = row[0]

for station in targets.keys():
    sql = """SELECT avg(max_tmpf) as high, avg(min_tmpf) as low 
        from summary_%s s, stations t WHERE (t.network ~* 'ASOS' or t.network ~* 'AWOS') 
        and day = '%s' and distance(t.geom, 'SRID=4326;POINT(%s %s)') < 2.5 
        and max_tmpf > -90 and min_tmpf < 90 and max_dwpf > -90 and min_dwpf < 90
        and t.iemid = s.iemid
        """ % (ts.year, day, nt.sts[station]['lon'], nt.sts[station]['lat'])
    icursor.execute(sql)
    row = icursor.fetchone()
    high = row[0]
    low = row[1]
    dwpf = (high + low) / 2.0

    sql = """UPDATE climate_sectors SET high = %s, low = %s, wvl = %s,
     dewp = %s, drct = 0 WHERE sector = %s and day = '%s'""" % (high, low, 
                                        wvl, dwpf, targets[station], day)
    wcursor.execute(sql)

wcursor.close()
WEPP.commit()
WEPP.close()
