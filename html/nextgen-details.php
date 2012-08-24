<?php 
include("../etc/config.inc.php");
$lat = isset($_REQUEST['lat'])? floatval($_REQUEST['lat']): die();
$lon = isset($_REQUEST['lon'])? floatval($_REQUEST['lon']): die();
$date = isset($_REQUEST['date'])? strtotime($_REQUEST['date']): die();
$year = date("Y", $date);

if ($lon < -96.639706  || $lat < 40.375437 || $lon > -90.140061 || $lat > 43.501196){
	echo "ERROR: Point outside of Iowa...";
	die();
}
$dbconn = pg_connect($weppdb);
$rs = pg_prepare($dbconn, "SELECT", "SELECT model_twp, county from iatwp WHERE 
		ST_Within(ST_GeomFromText($1, 4326), ST_Transform(the_geom,4326))
		and model_twp != 'None'");
$rs = pg_execute($dbconn, "SELECT", Array('POINT('.$lon .' '. $lat .')'));
if (pg_num_rows($rs) != 1){
	echo "ERROR: No township found!";
	die();
}
$row = pg_fetch_assoc($rs,0);
$model_twp = $row["model_twp"];
$county = $row["county"];

echo "<strong>Township:</strong> $model_twp";
echo "<br /><strong>County:</strong> $county";
echo "<br /><strong>Date:</strong> ". date("d M Y", $date);

/* Get monthly total */
$rs = pg_prepare($dbconn, "RAINFALL2", "select avg(rainfall) / 25.4 as rainfall
		from monthly_rainfall_$year
		WHERE valid = $1 and hrap_i IN
		(select distinct hrap_i from combos WHERE model_twp = $2)");
$rs = pg_execute($dbconn, "RAINFALL2", Array(date("Y-m-01", $date), $model_twp));
if (pg_num_rows($rs) == 0){
	echo "<br /><strong>Month Rainfall:</strong> Missing";
} else{
	$row = pg_fetch_assoc($rs, 0);
	echo "<br /><strong>Month Rainfall:</strong> ". sprintf("%.2f in", $row["rainfall"]);
}

/* Get monthly total */
$rs = pg_prepare($dbconn, "RAINFALL3", "select avg(rainfall) / 25.4 as rainfall
		from yearly_rainfall
		WHERE valid = $1 and hrap_i IN
		(select distinct hrap_i from combos WHERE model_twp = $2)");
$rs = pg_execute($dbconn, "RAINFALL3", Array(date("Y-01-01", $date), $model_twp));
if (pg_num_rows($rs) == 0){
	echo "<br /><strong>$year Rainfall:</strong> Missing";
} else{
	$row = pg_fetch_assoc($rs, 0);
	echo "<br /><strong>$year Rainfall:</strong> ". sprintf("%.2f in", $row["rainfall"]);
}

/* Fetch Results */
$rs = pg_prepare($dbconn, "RES", "select * from results_by_twp WHERE 
		valid = $1 and model_twp = $2");
$rs = pg_execute($dbconn, "RES", Array(date("Y-m-d", $date), $model_twp));
if (pg_num_rows($rs) == 0){
	echo "<br /><strong>Erosion Results are missing!</strong>";
} else{
	$row = pg_fetch_assoc($rs, 0);
	echo "<br /><strong>Avg Rainfall:</strong> ". sprintf("%.2f in", $row["avg_precip"] / 25.4);
	echo "<br /><strong>Soil Displacement:</strong> ". sprintf("%.2f T/A", $row["avg_loss"] * 4.463);
	echo "<br /><strong>Avg Runoff:</strong> ". sprintf("%.2f in", $row["avg_runoff"] / 25.4);
}

/* Get top events */
$rs = pg_prepare($dbconn, "TRES", "select valid from results_by_twp WHERE
		model_twp = $1 and valid > '2002-01-01' ORDER by avg_loss DESC LIMIT 10");
$rs = pg_execute($dbconn, "TRES", Array($model_twp));
if (pg_num_rows($rs) == 0){
	echo "<br /><strong>Top events are missing!</strong>";
} else{
	echo "<br /><strong>Top 10 Events:</strong> ";
	for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
		$ts = strtotime($row["valid"]);
		echo sprintf("<a href='javascript:setDate(%s,%s,%s);'>%s</a>, ",
				date("Y", $ts), date("m", $ts), date("d", $ts),
				date("M d, Y", $ts));
	}
}

?>