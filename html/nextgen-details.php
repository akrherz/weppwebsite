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
if (pg_num_rows($rs) == 0){
	echo "ERROR: No township found!";
	die();
}
$row = pg_fetch_assoc($rs,0);
$model_twp = $row["model_twp"];
$county = $row["county"];

echo "<strong>Township:</strong> $model_twp";
echo "<br /><strong>County:</strong> $county";
echo "<br /><strong>Date:</strong> ". date("d M Y", $date);

/* Get precip total for date */
$rs = pg_prepare($dbconn, "RAINFALL", "select avg(rainfall) / 25.4 as rainfall
		from daily_rainfall_$year
		WHERE valid = $1 and hrap_i IN
		(select distinct hrap_i from combos WHERE model_twp = $2)");
$rs = pg_execute($dbconn, "RAINFALL", Array(date("Y-m-d", $date), $model_twp));
if (pg_num_rows($rs) == 0){
	echo "<br /><strong>Avg Rainfall:</strong> Missing";
} else{
	$row = pg_fetch_assoc($rs, 0);
	echo "<br /><strong>Avg Rainfall:</strong> ". sprintf("%.2f in", $row["rainfall"]);
	
}

?>