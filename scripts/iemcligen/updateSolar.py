'''
 A straight copy of ISUAG solar radiation data to IDEPv1 climate sector data,
 if data is not found from the ISUAG network, then the previous year's value
 is used.  Lame yes, but will be improved with IDEPv2
'''
import psycopg2
ISUAG = psycopg2.connect(database='isuag', host='iemdb')
icursor = ISUAG.cursor()
WEPP = psycopg2.connect(database='wepp', host='iemdb')
wcursor = WEPP.cursor()
import sys
import datetime


cref = {'A131299': 1, 'A134309': 2, 'A135879': 3, 
        'A131299': 4, 'A130209': 5, 'A135849': 6,
        'A134759': 7, 'A131559': 8, 'A131909': 9}

# c80 is solar rad
def process(ts):
    for st in cref.keys():
        tbl = "daily"
        sector = cref[st]
        day = ts.strftime("%Y-%m-%d")
        sql = """SELECT c80 from %s WHERE valid = '%s' and station = '%s'""" % (
                                        tbl, day, st)
        icursor.execute(sql)
        if icursor.rowcount == 0:
            print "Missing Solar for sector: %s station: %s" % (sector, st)
            continue
        row = icursor.fetchone()
        wcursor.execute("""UPDATE climate_sectors SET rad = %s 
          WHERE day = %s and sector = %s """, (row[0], day, sector))

#"""
if __name__ == '__main__':
    ts = datetime.datetime.now() - datetime.timedelta(days=1)
    if len(sys.argv) == 4:
        ts = datetime.datetime( int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    process(ts)

    wcursor.close()
    WEPP.commit()
    WEPP.close()