'''
 Previous processing has left our 'results' table in the database with the 
 individual erosion data.  This script summarizes this for a particular date
'''
import sys
import datetime

import psycopg2
WEPP = psycopg2.connect(database='wepp', host='iemdb')
wcursor = WEPP.cursor()

def get_twp_counts():
    ''' Compute the counts of hrap and NRI points per township '''
    res = {}

    wcursor.execute("""select count(distinct(nri_id)), model_twp from combos 
        GROUP by model_twp""")
    for row in wcursor:
        res[ row[1] ] = {'nricnt': row[0], 'hrapcnt': 0 }

    # Count numer of HRAP cells per township
    wcursor.execute("""select count(distinct(hrap_i)), model_twp from combos 
        GROUP by model_twp""")
    for row in wcursor:
        res[ row[1] ]['hrapcnt'] = row[0]

    return res

def main(year, month, day):
    ''' Run for a particular year, month, and day '''
    ts = datetime.date(year, month, day)
    wcursor.execute("DELETE from results_by_twp WHERE valid = %s", (ts,) )

    # Count number of NRI points per township
    twpCnt = get_twp_counts()

    # First we load up our combos
    wcursor.execute("SELECT id, model_twp, hrap_i from combos")
    cDict = {}
    rainDict = {}
    for row in wcursor:
        cDict[ row[0] ] = {'model_twp': row[1], 'hrap_i': row[2] }
        rainDict[ row[2] ] = 0

    # Then we need to get our rainfall totals...
    wcursor.execute("""SELECT hrap_i, rainfall from daily_rainfall 
        WHERE valid = %s""", (ts, ))
    for row in wcursor:
        rainDict[ row[0] ] = row[1]

    # Then we load up our results
    wcursor.execute("""SELECT run_id, valid, runoff, loss, precip from results 
        WHERE valid = %s""", (ts,))
    rDict = {}
    for row in wcursor:
        rDict[ row[0] ] = {'valid': row[1], 'runoff': row[2], 'loss': row[3],
                           'precip': row[4]}


    # Now we compute township stuff
    twpDict = {}
    for comboid in cDict.keys():
        model_twp = cDict[comboid]['model_twp']
        hrap_i = cDict[comboid]['hrap_i']
        if not twpDict.has_key(model_twp):
            twpDict[model_twp] = {'truns':0, 'run_points':0, 
                        'trunoff':0, 'tloss':0, 'avg_runoff':0, 'avg_loss':0,
                        'train': 0, 'max_precip': 0, 'min_precip': 999,
                        'min_loss': 999, 'max_loss': 0, 'loss': [],
                        'min_runoff': 999, 'max_runoff': 0, 'runoff': []}
        if rDict.has_key(comboid):
            ro = rDict[comboid]["runoff"]
            lo = rDict[comboid]["loss"]
            twpDict[model_twp]['run_points'] += 1
            twpDict[model_twp]['trunoff'] += ro
            twpDict[model_twp]['tloss'] += lo
            twpDict[model_twp]['loss'].append(lo)
            twpDict[model_twp]['runoff'].append(ro)
            twpDict[model_twp]['max_runoff'] = max(ro, 
                                            twpDict[model_twp]['max_runoff'])
            twpDict[model_twp]['min_runoff'] = min(ro, 
                                            twpDict[model_twp]['min_runoff'])
            twpDict[model_twp]['max_loss'] = max(lo, 
                                            twpDict[model_twp]['max_loss'])
            twpDict[model_twp]['min_loss'] = min(lo, 
                                            twpDict[model_twp]['min_loss'])
        else:
            twpDict[model_twp]['loss'].append(0)
            twpDict[model_twp]['runoff'].append(0)
            twpDict[model_twp]['min_loss'] = 0
            twpDict[model_twp]['min_runoff'] = 0


        twpDict[model_twp]['train'] += rainDict[hrap_i]
        twpDict[model_twp]['max_precip'] = max(rainDict[hrap_i],
                                            twpDict[model_twp]['max_precip'])
        twpDict[model_twp]['min_precip'] = min(rainDict[hrap_i],
                                            twpDict[model_twp]['min_precip'])
        twpDict[model_twp]['truns'] += 1

    # Now we compute the averages
    for model_twp in twpDict.keys():
        if twpDict[model_twp]['min_loss'] == 999:
            twpDict[model_twp]['min_loss'] = 0
        if twpDict[model_twp]['min_runoff'] == 999:
            twpDict[model_twp]['min_runoff'] = 0
        truns = float(twpDict[model_twp]['truns'])
        twpDict[model_twp]['model_twp'] = model_twp
        twpDict[model_twp]['valid'] = ts.strftime("%Y-%m-%d")
        twpDict[model_twp]['avg_precip'] = twpDict[model_twp]['train'] / truns
        twpDict[model_twp]['avg_runoff'] = twpDict[model_twp]['trunoff'] / truns
        twpDict[model_twp]['avg_loss'] = twpDict[model_twp]['tloss'] / truns
        lo_avg = twpDict[model_twp]['avg_loss']
        ro_avg = twpDict[model_twp]['avg_runoff']
        ht = float(twpCnt[model_twp]['hrapcnt'])
        nt = float(twpCnt[model_twp]['nricnt'])
        if ht >= 2 and nt >= 2:
            tot = 0
            for lo in twpDict[model_twp]['loss']:
                tot += ( float(lo) - lo_avg)**2
                
            twpDict[model_twp]['ve_loss'] = ((1.0 / (ht * nt)) 
                * (1.0 / (ht - 1.0)) * (1.0 / (nt - 1.0) ) * tot )
            tot = 0
            for ro in twpDict[model_twp]['runoff']:
                tot += ( float(ro) - ro_avg)**2
            twpDict[model_twp]['ve_runoff'] = ((1.0 / (ht * nt))  
                * (1.0 / (ht - 1.0)) * (1.0 / (nt - 1.0) ) * tot )
        else:
            twpDict[model_twp]['ve_loss'] = 0
            twpDict[model_twp]['ve_runoff'] = 0

        # Now we insert values!
        wcursor.execute("""INSERT into results_by_twp(model_twp, valid, 
        avg_precip, max_precip, min_loss, avg_loss, max_loss, min_runoff, 
        avg_runoff, max_runoff, run_points, min_precip, ve_loss, ve_runoff ) 
        values ('%(model_twp)s', '%(valid)s', 
        %(avg_precip)s, %(max_precip)s, %(min_loss)s, %(avg_loss)s,
        %(max_loss)s, %(min_runoff)s, %(avg_runoff)s, 
        %(max_runoff)s, %(run_points)s, %(min_precip)s, %(ve_loss)s, 
        %(ve_runoff)s )""" % twpDict[model_twp] )

    # Now we update the yearly totals...  Delete old records first
    wcursor.execute("""DELETE from results_twp_year WHERE   
         valid = %s""", (ts, ))

    sql = """insert into results_twp_year (model_twp, valid, avg_loss, 
        avg_runoff, min_loss, max_loss, min_runoff, 
        max_runoff, ve_runoff, ve_loss) 
         select model_twp, '%s-01-01', 
         sum(avg_loss), 
         sum(avg_runoff), 
         0, 
         max(avg_loss), 
         0, 
         max(min_runoff),
         sum(ve_runoff), 
         sum(ve_loss) from results_by_twp 
         WHERE valid  >= '%s-01-01' and valid <= '%s-12-31' 
         GROUP by model_twp""" % (ts.year, ts.year, ts.year)
    wcursor.execute(sql)

    # Now we update the monthly totals... Delete old records first
    wcursor.execute("""DELETE from results_twp_month WHERE 
         valid = %s""", (ts, ))

    sql = """insert into results_twp_month (model_twp, valid, avg_loss, avg_runoff,
    min_loss, max_loss, min_runoff, max_runoff, ve_runoff, ve_loss) 
     select model_twp, '%s', 
     sum(avg_loss), 
     sum(avg_runoff), 
     0, 
     max(avg_loss), 
     0, 
     max(min_runoff), 
     sum(ve_runoff), 
     sum(ve_loss) from results_by_twp 
     WHERE extract(year from valid) = %s and 
     extract(month from valid) = %s GROUP by model_twp""" % (
                                ts.strftime("%Y-%m-01"), ts.year, ts.month)
    wcursor.execute(sql)


if __name__ == '__main__':
    ''' See how we are called '''
    if len(sys.argv) == 4:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
        now = datetime.datetime(year, month, day)
    else:
        now = datetime.datetime.now() - datetime.timedelta(days=1)
  
    main(now.year, now.month, now.day)
    wcursor.close()
    WEPP.commit()
    WEPP.close()