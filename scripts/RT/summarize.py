#!/mesonet/python/bin/python
# Need a script to compute the township level results
# Daryl Herzmann 27 Apr 2004
# 25 Aug 2004  Stupid error that was calling this script for the wrong date
#  8 Mar 2005  Add in support for updating the yearly totals...
#  4 May 2005	Update more fields on monthly and yearly totals

import sys, mx.DateTime

import pg
weppdb = pg.connect('wepp', 'iemdb')

def Main(_YEAR, _MONTH, _DAY):
  _ts = mx.DateTime.DateTime(_YEAR, _MONTH, _DAY)
  sqldate = _ts.strftime("%Y-%m-%d")
  weppdb.query("DELETE from results_by_twp WHERE valid = '%s'" % (sqldate, ) )

  # Now we get to work...

  # Count number of NRI points per township
  twpCnt = {}
  sql = "select count(distinct(nri_id)), model_twp from combos \
    GROUP by model_twp"
  rs = weppdb.query(sql).dictresult()
  for i in range(len(rs)):
    twpCnt[ rs[i]['model_twp'] ] = {'nricnt': int(rs[i]['count']),
      'hrapcnt': 0 }
  del(rs)

  # Count numer of HRAP cells per township
  sql = "select count(distinct(hrap_i)), model_twp from combos \
    GROUP by model_twp"
  rs = weppdb.query(sql).dictresult()
  for i in range(len(rs)):
    twpCnt[ rs[i]['model_twp'] ]['hrapcnt'] = int(rs[i]['count'])


  # First we load up our combos
  sql = "SELECT id, model_twp, hrap_i from combos"
  combos = weppdb.query(sql).dictresult()
  cDict = {}
  rainDict = {}
  for i in range(len(combos)):
    cDict[ int(combos[i]["id"]) ] = {
      'model_twp': combos[i]["model_twp"],
      'hrap_i': combos[i]['hrap_i'] }
    rainDict[ int(combos[i]["hrap_i"]) ] = 0
  del(combos)

  # Then we need to get our rainfall totals...
  sql = "SELECT hrap_i, rainfall from daily_rainfall_%s \
    WHERE valid = '%s'" % (_ts.year, _ts.strftime("%Y-%m-%d") )
  r = weppdb.query(sql).dictresult()
  for i in range(len(r)):
    rainDict[ int(r[i]['hrap_i']) ] = float(r[i]['rainfall'])
  del(r)


  # Then we load up our results
  results = weppdb.query("SELECT * from results WHERE \
    valid = '%s' " % (_ts.strftime("%Y-%m-%d"),) ).dictresult()
  rDict = {}
  for i in range(len(results)):
    rDict[ int(results[i]["run_id"]) ] = results[i]
  del(results)


  # Now we compute township stuff
  twpDict = {}
  for comboid in cDict.keys():
    model_twp = cDict[comboid]['model_twp']
    hrap_i = cDict[comboid]['hrap_i']
    if (not twpDict.has_key(model_twp)):
      twpDict[model_twp] = {'truns':0, 'run_points':0, 
      'trunoff':0, 'tloss':0, 'avg_runoff':0, 'avg_loss':0,
      'train': 0, 'max_precip': 0, 'min_precip': 999,
      'min_loss': 999, 'max_loss': 0, 'loss': [],
      'min_runoff': 999, 'max_runoff': 0, 'runoff': []}
    if (rDict.has_key(comboid)):
      ro = rDict[comboid]["runoff"]
      lo = rDict[comboid]["loss"]
      twpDict[model_twp]['run_points'] += 1
      twpDict[model_twp]['trunoff'] += ro
      twpDict[model_twp]['tloss'] += lo
      twpDict[model_twp]['loss'].append(lo)
      twpDict[model_twp]['runoff'].append(ro)
      if ( ro > twpDict[model_twp]['max_runoff']):
        twpDict[model_twp]['max_runoff'] = ro
      if ( ro < twpDict[model_twp]['min_runoff']):
        twpDict[model_twp]['min_runoff'] = ro

      if ( lo > twpDict[model_twp]['max_loss']):
        twpDict[model_twp]['max_loss'] = lo
      if ( lo < twpDict[model_twp]['min_loss']):
        twpDict[model_twp]['min_loss'] = lo

    else:
      twpDict[model_twp]['loss'].append(0)
      twpDict[model_twp]['runoff'].append(0)
      twpDict[model_twp]['min_loss'] = 0
      twpDict[model_twp]['min_runoff'] = 0


    twpDict[model_twp]['train'] += rainDict[hrap_i]

    if (rainDict[hrap_i] > twpDict[model_twp]['max_precip']):
      twpDict[model_twp]['max_precip'] = rainDict[hrap_i]

    if (rainDict[hrap_i] < twpDict[model_twp]['min_precip']):
      twpDict[model_twp]['min_precip'] = rainDict[hrap_i]

    twpDict[model_twp]['truns'] += 1

  # Now we compute the averages
  for model_twp in twpDict.keys():
    if (twpDict[model_twp]['min_loss'] == 999):
      twpDict[model_twp]['min_loss'] = 0
    if (twpDict[model_twp]['min_runoff'] == 999):
      twpDict[model_twp]['min_runoff'] = 0
    twpDict[model_twp]['model_twp'] = model_twp
    twpDict[model_twp]['valid'] = _ts.strftime("%Y-%m-%d")
    twpDict[model_twp]['avg_precip'] = twpDict[model_twp]['train'] / float(twpDict[model_twp]['truns'])
    twpDict[model_twp]['avg_runoff'] = twpDict[model_twp]['trunoff'] / float(twpDict[model_twp]['truns'])
    twpDict[model_twp]['avg_loss'] = twpDict[model_twp]['tloss'] / float(twpDict[model_twp]['truns'])
    lo_avg = twpDict[model_twp]['avg_loss']
    ro_avg = twpDict[model_twp]['avg_runoff']
    ht = float(twpCnt[model_twp]['hrapcnt'])
    nt = float(twpCnt[model_twp]['nricnt'])
    if (ht >= 2 and nt >= 2):
      tot = 0
      for lo in twpDict[model_twp]['loss']:
        tot += ( float(lo) - lo_avg)**2
      twpDict[model_twp]['ve_loss'] = (1.0 / (ht * nt)) \
        * (1.0 / (ht - 1.0)) * (1.0 / (nt - 1.0) ) * tot
      tot = 0
      for ro in twpDict[model_twp]['runoff']:
        tot += ( float(ro) - ro_avg)**2
      twpDict[model_twp]['ve_runoff'] = (1.0 / (ht * nt)) \
        * (1.0 / (ht - 1.0)) * (1.0 / (nt - 1.0) ) * tot
    else:
      twpDict[model_twp]['ve_loss'] = 0
      twpDict[model_twp]['ve_runoff'] = 0

    # Now we insert values!
    weppdb.query("INSERT into results_by_twp(model_twp, valid, avg_precip,\
      max_precip, min_loss, avg_loss, max_loss, min_runoff, avg_runoff,\
      max_runoff, run_points, min_precip, ve_loss, ve_runoff ) values \
      ('%(model_twp)s', '%(valid)s', \
      %(avg_precip)s, %(max_precip)s, %(min_loss)s, %(avg_loss)s,\
      %(max_loss)s, %(min_runoff)s, %(avg_runoff)s, \
      %(max_runoff)s, %(run_points)s, %(min_precip)s, %(ve_loss)s, \
      %(ve_runoff)s )" \
      % twpDict[model_twp] )

  # Now we update the yearly totals...  Delete old records first
  sql = "DELETE from results_twp_year WHERE \
         valid = '%s'" % (_ts.strftime("%Y-01-01"), )
  weppdb.query(sql)

  sql = "insert into results_twp_year (model_twp, valid, avg_loss, avg_runoff, \
    min_loss, max_loss, min_runoff, max_runoff, ve_runoff, ve_loss) \
     select model_twp, '%s-01-01', \
     sum(avg_loss), \
     sum(avg_runoff), \
     0, \
     max(avg_loss), \
     0, \
     max(min_runoff), \
     sum(ve_runoff), \
     sum(ve_loss) from results_by_twp \
    WHERE extract(year from valid) = %s GROUP by model_twp" \
    % (_ts.year, _ts.year)
  weppdb.query(sql)

  # Now we update the monthly totals... Delete old records first
  sql = "DELETE from results_twp_month WHERE \
         valid = '%s'" % (_ts.strftime("%Y-%m-01"), )
  weppdb.query(sql)

  sql = "insert into results_twp_month (model_twp, valid, avg_loss, avg_runoff,\
    min_loss, max_loss, min_runoff, max_runoff, ve_runoff, ve_loss) \
     select model_twp, '%s', \
     sum(avg_loss), \
     sum(avg_runoff), \
     0, \
     max(avg_loss), \
     0, \
     max(min_runoff), \
     sum(ve_runoff), \
     sum(ve_loss) from results_by_twp \
     WHERE extract(year from valid) = %s and \
     extract(month from valid) = %s GROUP by model_twp" \
    % (_ts.strftime("%Y-%m-01"), _ts.year, _ts.month)
  weppdb.query(sql)
#"""
if (len(sys.argv) == 4):
  _YEAR = int(sys.argv[1])
  _MONTH = int(sys.argv[2])
  _DAY = int(sys.argv[3])
  now = mx.DateTime.DateTime(_YEAR, _MONTH, _DAY)
else:
  now = mx.DateTime.now() + mx.DateTime.RelativeDateTime(days=-1)
  


Main(now.year, now.month, now.day)
"""

sts = mx.DateTime.DateTime(2006,1,1)
ets = mx.DateTime.DateTime(2006,4,12)
interval = mx.DateTime.RelativeDateTime(days=+1)
now = sts

while (now < ets):
  print now
  Main(now.year, now.month, now.day)
  now += interval
"""
