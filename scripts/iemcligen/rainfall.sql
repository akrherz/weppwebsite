DELETE from monthly_rainfall_2012 WHERE valid = '2012-08-01';
DELETE from daily_rainfall_2012 WHERE valid = '2012-08-12';
COPY daily_rainfall_2012 FROM stdin;
\.
DELETE from rainfall_log WHERE valid = '2012-08-12' ;
INSERT into rainfall_log (valid, max_rainfall) values ( 
	'2012-08-12', 0) ;
INSERT into monthly_rainfall_2012 (hrap_i, valid, rainfall,
		peak_15min, hr_cnt) 
        SELECT hrap_i, '2012-08-01', sum(rainfall), max(peak_15min), sum(hr_cnt) 
		from daily_rainfall_2012 WHERE 
        valid >= '2012-08-01' and valid < '2012-09-01' GROUP by hrap_i;
DELETE from yearly_rainfall WHERE valid = '2012-01-01';
INSERT into yearly_rainfall (hrap_i, valid, rainfall,
		peak_15min, hr_cnt) 
		SELECT hrap_i, '2012-01-01', sum(rainfall), max(peak_15min), sum(hr_cnt) 
		from monthly_rainfall_2012 GROUP by hrap_i;
