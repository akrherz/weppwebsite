<?php
/* Something to generate the plots! */

include_once("../../etc/config.inc.php");
dl($mapscript);

if (isset($argv))
   for ($i=1;$i<count($argv);$i++)
   {
       $it = split("=",$argv[$i]);
       $_GET[$it[0]] = $it[1];
   }
//print_r($_GET);
//die();

/* stuff that we need to $_GET[] */
$dstr = isset($_GET["dstr"]) ? $_GET["dstr"] : date("m/d/Y", time() - 86400);
$tokens = explode("/", $dstr);
$year = $tokens[2];
$month = $tokens[0];
$day = $tokens[1];

$extents = isset($_GET['extents']) ? $_GET['extents'] : 
		"160000, 4450000, 760000, 4850000";
$layers = isset($_GET['layers']) ? $_GET['layers'] : 
		Array("background", "states", "counties");
$var = isset($_GET['var']) ? $_GET['var'] : "rainfall_in";
$map_height = isset($_GET['height']) ? $_GET['height'] : 480;
$map_width = isset($_GET['width']) ? $_GET['width'] : 640;
$advanced = isset($_GET["advanced"]) ? 1 : 0;
$duration = isset($_GET["duration"]) ? $_GET["duration"] : 'daily';

/* Time related stuff */
$ts = mktime(0,0,0, $month, $day, $year);

/* Color table, blue to brown */
$c = Array();
$c[0] = Array('r'=>  0,'g'=>   0,'b'=> 255); // 
$c[1] = Array('r'=>  0,'g'=> 102,'b'=> 255); // 
$c[2] = Array('r'=>  0,'g'=> 212,'b'=> 255); // 
$c[3] = Array('r'=> 24,'g'=> 255,'b'=> 255); // 
$c[4] = Array('r'=>102,'g'=> 255,'b'=> 153); // 
$c[5] = Array('r'=> 51,'g'=> 255,'b'=>   0); // 
$c[6] = Array('r'=>204,'g'=> 255,'b'=>   0); // 
$c[7] = Array('r'=>255,'g'=> 255,'b'=>   0); // 
$c[8] = Array('r'=>255,'g'=> 232,'b'=>   0); // 
$c[9] = Array('r'=>255,'g'=> 204,'b'=>   0); // 
$c[10] = Array('r'=>255,'g'=>153,'b'=>   0); // 
$c[11] = Array('r'=>255,'g'=>102,'b'=>   0); // 

$cr = array_reverse($c);

$ramps = Array(
	0 =>  Array(0.05, 0.1, 0.25, 0.5, 0.75, 1, 1.5, 2,3,5,7), // Rainfall (inch)
	1 => Array(0.5, 1, 2, 3, 4, 6, 8, 10,11,12,13),
	2 => Array(1, 2, 4, 6, 8, 10, 12, 14,16,18,20),   // Precip(hours)
	3 => Array(1, 2, 5, 10, 15, 20, 30, 40, 50, 75,100),  // Precip(mm)
	4 => Array(4, 8, 12, 16, 20, 25, 30, 35,36,37,38),
	5 => Array(5, 10, 20, 40, 60, 100, 120, 160,161,162,163),
	6 => Array(10, 25, 50, 75, 100, 150, 200, 250,251,252,253),
	7 => Array(100, 200, 300, 400, 500, 600, 800, 1000,1001,1002,1003),
	8 => Array(0.1, 0.25, 0.5, 1, 1.5, 2, 3, 5,6,7,8),           // Precip(in)
    9 => Array(150, 200, 250, 300, 350, 400,450,500,550,600,650),   // TSW
	10 => Array(-100, -75, -50, -25, -10, 0, 10, 25, 50, 75,100),
	11 => Array(0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50),
	12 => Array(-30, -20, -15, -10, -5, 0, 5, 10, 15, 20,30),
);
$mo_ramps = Array(
	0 =>  Array(0.1, 0.5, 1, 2, 4, 8, 16, 24,25,26,27),
	1 => Array(0.5, 1, 2, 3, 4, 6, 8, 10,11,12,13),
	2 => Array(1, 2, 4, 6, 8, 10, 12, 20,21,22,23),
	3 => Array(10, 25, 50, 75, 100, 150, 200, 250,251,252,253),
	4 => Array(4, 8, 12, 16, 20, 25, 30, 35,36,37,38),
	5 => Array(5, 10, 20, 40, 60, 100, 120, 160,161,162,163),
	6 => Array(10, 25, 50, 75, 100, 150, 200, 250,251,252,253),
	7 => Array(100, 200, 300, 400, 500, 600, 800, 1000,1001,1002,1003),
	8 => Array(0.1, 0.5, 1, 2, 3, 5, 7, 10,11,12,13)
);

$yr_ramps = Array(
	0 =>  Array(0.1, 0.5, 1, 2, 4, 8, 16, 24,25,26,27),
	1 => Array(0.5, 1, 2, 3, 4, 6, 8, 10,11,12,13),
	2 => Array(1, 2, 4, 6, 8, 10, 12, 20,21,22,23),
	3 => Array(100, 200, 300, 400, 500, 750, 1000, 1250,1251,1252,1253),
	4 => Array(4, 8, 12, 16, 20, 25, 30, 35,36,37,38),
	5 => Array(5, 10, 20, 40, 60, 100, 120, 160,161,162,163),
	6 => Array(10, 25, 50, 75, 100, 150, 200, 250,251,252,253),
	7 => Array(100, 200, 300, 400, 500, 600, 800, 1000,1001,1002,1003),
	8 => Array(1, 2, 6, 10, 14, 18, 22, 26,27,28,29)
);

$params = Array(
"vsm_7day" => Array('dbstr' => 'bogus',
  'units' => '%', 'cramp' => $cr,
  'title' => "7 Day Soil Water Change Ending: ",
  'table' => "bogus", 'myramp' => 10,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select h.the_geom, h.oid, da  from 
          (select o.model_twp, o.vsm - t.vsm as da 
           from waterbalance_by_twp o, waterbalance_by_twp t 
           WHERE o.model_twp = t.model_twp 
           and o.valid = '". strftime("%Y-%m-%d", $ts) ."' 
        and t.valid = ('". strftime("%Y-%m-%d", $ts) ."'::date - '7 days'::interval) 
           ) as foo 
          left join iatwp h using (model_twp)) as foo2
          USING unique oid using srid=26915"),

"vsm_1month" => Array('dbstr' => 'bogus',
  'units' => '%', 'cramp' => $cr,
  'title' => "1 Month Soil Water Change Ending: ",
  'table' => "bogus", 'myramp' => 10,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select h.the_geom, h.oid, da  from 
          (select o.model_twp, o.vsm - t.vsm as da 
           from waterbalance_by_twp o, waterbalance_by_twp t 
           WHERE o.model_twp = t.model_twp 
           and o.valid = '". strftime("%Y-%m-%d", $ts) ."' 
        and t.valid = ('". strftime("%Y-%m-%d", $ts) ."'::date - '1 month'::interval) 
           ) as foo 
          left join iatwp h using (model_twp)) as foo2
          USING unique oid using srid=26915"),

"vsm_3month" => Array('dbstr' => 'bogus',
  'units' => '%', 'cramp' => $cr,
  'title' => "3 Month Soil Water Change Ending: ",
  'table' => "bogus", 'myramp' => 12,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select h.the_geom, h.oid, da  from 
          (select o.model_twp, o.vsm - t.vsm as da 
           from waterbalance_by_twp o, waterbalance_by_twp t 
           WHERE o.model_twp = t.model_twp 
           and o.valid = '". strftime("%Y-%m-%d", $ts) ."' 
        and t.valid = ('". strftime("%Y-%m-%d", $ts) ."'::date - '3 months'::interval) 
           ) as foo 
          left join iatwp h using (model_twp)) as foo2
          USING unique oid using srid=26915"),

"vsm_1year" => Array('dbstr' => 'bogus',
  'units' => '%', 'cramp' => $cr,
  'title' => "1 Year Soil Water Change Ending: ",
  'table' => "bogus", 'myramp' => 10,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts),
  'sql' => "the_geom from (select h.the_geom, h.oid, da  from 
          (select o.model_twp, o.vsm - t.vsm as da 
           from waterbalance_by_twp o, waterbalance_by_twp t 
           WHERE o.model_twp = t.model_twp 
           and o.valid = '". strftime("%Y-%m-%d", $ts) ."' 
        and t.valid = ('". strftime("%Y-%m-%d", $ts) ."'::date - '1 year'::interval) 
           ) as foo 
          left join iatwp h using (model_twp)) as foo2
          USING unique oid using srid=26915"),


"vsm_stddev" => Array('dbstr' => 'vsm_stddev',
  'units' => '%', 'cramp' => $c,
  'title' => "STDDEV Total Soil Water on ",
  'table' => "waterbalance_by_twp", 'myramp' => 5,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"vsm_range" => Array('dbstr' => 'vsm_range',
  'units' => '%','cramp' => $c,
  'title' => "Range of Total Soil Water on ",
  'table' => "waterbalance_by_twp", 'myramp' => 6,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"vsm" => Array('dbstr' => 'vsm',
  'units' => '% in Root Zone', 'cramp' => $cr,
  'title' => "Volumetric Soil Water on ",
  'table' => "waterbalance_by_twp", 'myramp' => 11,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"s10cm_mm" => Array('dbstr' => 's10cm',   'units' => 'mm in top 10cm', 'cramp' => $cr,
  'title' => "0-10cm Soil Water on ",
  'table' => "waterbalance_by_twp", 'myramp' => 11,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"s20cm_mm" => Array('dbstr' => 's20cm',   'units' => 'mm in 10-20cm layer', 'cramp' => $cr,
  'title' => "10-20cm Soil Water on ",
  'table' => "waterbalance_by_twp", 'myramp' => 11,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),


"rainfall_in" => Array('dbstr' => 'rainfall / 25.4',
  'units' => 'inches', 'cramp' => $c,
  'title' => "Estimated Rainfall on ",
  'table' => "daily_rainfall_$year", 'myramp' => 8,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"rainfall_mm" => Array('dbstr' => 'rainfall',
  'units' => 'millimeters', 'cramp' => $c,
  'title' => "Estimated Rainfall on ",
  'table' => "daily_rainfall_$year", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"peak_15min_in" => Array('dbstr' => '(peak_15min / 25.4) * 4.0',
  'units' => 'inches per hour', 'cramp' => $c,
  'title' => "Peak Rainfall Intensity on ",
  'table' => "daily_rainfall_$year", 'myramp' => 8,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"peak_15min_mm" => Array('dbstr' => '(peak_15min) * 4.0',
  'units' => 'millimeters per hour', 'cramp' => $c,
  'title' => "Peak Rainfall Intensity on ",
  'table' => "daily_rainfall_$year", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"time_" => Array('dbstr' => '(hr_cnt) / 4.0',
  'units' => 'hours', 'cramp' => $c,
  'title' => "Rainfall Duration: ",
  'table' => "daily_rainfall_$year", 'myramp' => 2,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"min_runoff_in" => Array('dbstr' => 'min_runoff / 25.4',
  'units' => 'inches', 'cramp' => $c,
  'title' => "Minimum Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"avg_runoff_in" => Array('dbstr' => 'avg_runoff / 25.4',
  'units' => 'inches', 'cramp' => $c,
  'title' => "Average Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"max_runoff_in" => Array('dbstr' => 'max_runoff / 25.4',
  'units' => 'inches', 'cramp' => $c,
  'title' => "Maximum Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"min_runoff_mm" => Array('dbstr' => 'min_runoff',
  'units' => 'millimeters', 'cramp' => $c,
  'title' => "Minimum Runoff: ",
  'table' => "results_by_twp", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"avg_runoff_mm" => Array('dbstr' => 'avg_runoff',
  'units' => 'millimeters', 'cramp' => $c,
  'title' => "Average Runoff: ",
  'table' => "results_by_twp", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"max_runoff_mm" => Array('dbstr' => 'max_runoff',
  'units' => 'millimeters', 'cramp' => $c,
  'title' => "Maximum Runoff: ",
  'table' => "results_by_twp", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"min_loss_acre" => Array('dbstr' => 'min_loss * 4.463',
  'units' => 'tons per acre', 'cramp' => $c,
  'title' => "Minimum Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"avg_loss_acre" => Array('dbstr' => 'avg_loss * 4.463',
  'units' => 'tons per acre', 'cramp' => $c,
  'title' => "Average Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"max_loss_acre" => Array('dbstr' => 'max_loss * 4.463',
  'units' => 'tons per acre', 'cramp' => $c,
  'title' => "Maximum Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"min_loss_hectare" => Array('dbstr' => 'min_loss * 10.0',
  'units' => 'tons per hectare', 'cramp' => $c,
  'title' => "Minimum Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 1,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"avg_loss_hectare" => Array('dbstr' => 'avg_loss * 10.0',
  'units' => 'tons per hectare', 'cramp' => $c,
  'title' => "Average Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 1,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"max_loss_hectare" => Array('dbstr' => 'max_loss * 10.0',
  'units' => 'tons per hectare', 'cramp' => $c,
  'title' => "Maximum Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 1,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"ve_runoff_in" => Array('dbstr' => 've_runoff / 25.4',
  'units' => 'inches', 'cramp' => $c,
  'title' => "Variance Estimator for Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"ve_runoff_mm" => Array('dbstr' => 've_runoff',
  'units' => 'millimeters', 'cramp' => $c,
  'title' => "Variance Estimator for Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"ve_loss_acre" => Array('dbstr' => 've_loss * 4.463',
  'units' => 'tons per acre', 'cramp' => $c,
  'title' => "Variance Estimator for Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"ve_loss_hectare" => Array('dbstr' => 've_loss * 10.0',
  'units' => 'tons per hectare', 'cramp' => $c,
  'title' => "Variance Estimator for Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

);
$param = $params[$var];
$param['ramp'] = $ramps[ $param['myramp'] ];
$var = "${duration}_$var";
if ($duration == "daily")
{
  $param["title"] .= strftime("%d %b %Y", $ts);
}
else if ($duration == "monthly")
  {
    $param["table"] = "results_twp_month";
    $param["dbdate"] = strftime("%Y-%m-01", $ts); 
  } 
else if ($duration == "yearly")
  {
    $param["table"] = "results_twp_year";
    $param["dbdate"] = strftime("%Y-01-01", $ts);
    $param['ramp'] = $yr_ramps[ $param['myramp'] ];
  }
/* Rainfall hacks */
if ($param["gtype"] == "hrap")
{
 if ($duration == "monthly")
 {
   $param["table"] = "monthly_rainfall_$year";
   $param["dbdate"] = strftime("%Y-%m-01", $ts);
   $param['ramp'] = $mo_ramps[ $param['myramp'] ];
 } else if ($duration == "yearly")
 {
   $param["table"] = "yearly_rainfall";
   $param["dbdate"] = strftime("%Y-01-01", $ts);
   $param['ramp'] = $yr_ramps[ $param['myramp'] ];
 }
}
/* Rainfall duration hacks */
if ($var == "monthly_time_" || $var == "yearly_time_")
{
   $param['dbstr'] = 'hr_cnt / 96.0';
   $param['units'] = 'days';
}


$pgconn = pg_connect($weppdb);
$a = explode("_", $var);
$logtable = "rainfall_log";
if ($param["gtype"] == "twp") $logtable = "erosion_log";

if ($a[0] == "daily")
{
	$q = "SELECT * from $logtable WHERE valid = '". $param["dbdate"] ."'";

} else if ($a[0] == "monthly")
{
	$q = "SELECT extract(day from max(valid)) as max_valid, 
		extract(day from min(valid)) as min_valid from
		$logtable WHERE extract(year from valid) = $year and
		extract(month from valid) = $month";
    $nicedate = date("M Y", $ts);
} else if ($a[0] == "yearly")
{
	$q = "SELECT max(valid) as max_valid, 
		min(valid) as min_valid from
		$logtable WHERE extract(year from valid) = $year";
}
$rs = pg_exec($pgconn, $q);

$missing = true;
if (($row = @pg_fetch_array($rs, 0))){
	if ($a[0] != "daily")
	{
		$param['title'] .= "[". $row["min_valid"] ." - ". $row["max_valid"] ."] ${nicedate}";
	}
	$missing = false;
}


/* Start Mapping */
$map = ms_newMapObj("$_BASE/data/gis/map/wepp.map");
$map->set("width", $map_width);
$map->set("height", $map_height);

/* Set Extents */
$arExtents = explode(",", $extents);
$map->setextent($arExtents[0], $arExtents[1], $arExtents[2], $arExtents[3]);


/* Prepare the Image */
$img = $map->prepareImage();

function add_and_draw($name)
{
	global $layers, $map, $img;
	if (in_array($name, $layers) )
	{
		$lyr = $map->getlayerbyname($name);
		$lyr->set("status", MS_ON );
		$lyr->draw($img);
	}
}

add_and_draw("background");
add_and_draw("states");

$colors = $param["cramp"];
if (! $missing )
{
$rainfall = $map->getlayerbyname($param["maplayer"]);
$rainfall->set("status", MS_ON);
if ($param["gtype"] == "hrap")
{
  $sql = "the_geom from (select d.oid as oid, 
   (". $param["dbstr"] .") as da, h.the_geom from 
   ". $param["table"] ." d left join hrap_polygons h using (hrap_i) 
   WHERE d.valid = '". $param["dbdate"] ."') as foo 
   using unique oid using srid=26915";
} else 
{
  $sql = "the_geom from (select d.oid as oid, 
   (". $param["dbstr"] .") as da, h.the_geom from 
   ". $param["table"] ." d left join iatwp h using (model_twp) 
   WHERE d.valid = '". $param["dbdate"] ."') as foo 
   using unique oid using srid=26915";

}
/* Custom data statements :) */
if (isset($param["sql"]))
{
  $rainfall->set("data", $param["sql"]);
} else 
{
  $rainfall->set("data", $sql);
}
$bins = $param["ramp"];

$cz = ms_newClassObj($rainfall);
$cz->setexpression("([DA] == 0)");

$c0 = ms_newClassObj($rainfall);
$c0->setexpression("([DA] < ". $bins[0] .")");
$c0s = ms_newStyleObj($c0);
$c0s->color->setRGB($colors[0]['r'], $colors[0]['g'], $colors[0]['b']);

$c1 = ms_newClassObj($rainfall);
$c1->setexpression("([DA] < ". $bins[1] .")");
$c1s = ms_newStyleObj($c1);
$c1s->color->setRGB($colors[1]['r'], $colors[1]['g'], $colors[1]['b']);

$c2 = ms_newClassObj($rainfall);
$c2->setexpression("([DA] < ". $bins[2] .")");
$c2s = ms_newStyleObj($c2);
$c2s->color->setRGB($colors[2]['r'], $colors[2]['g'], $colors[2]['b']);

$c3 = ms_newClassObj($rainfall);
$c3->setexpression("([DA] < ". $bins[3] .")");
$c3s = ms_newStyleObj($c3);
$c3s->color->setRGB($colors[3]['r'], $colors[3]['g'], $colors[3]['b']);

$c4 = ms_newClassObj($rainfall);
$c4->setexpression("([DA] < ". $bins[4] .")");
$c4s = ms_newStyleObj($c4);
$c4s->color->setRGB($colors[4]['r'], $colors[4]['g'], $colors[4]['b']);

$c5 = ms_newClassObj($rainfall);
$c5->setexpression("([DA] < ". $bins[5] .")");
$c5s = ms_newStyleObj($c5);
$c5s->color->setRGB($colors[5]['r'], $colors[5]['g'], $colors[5]['b']);

$c6 = ms_newClassObj($rainfall);
$c6->setexpression("([DA] < ". $bins[6] .")");
$c6s = ms_newStyleObj($c6);
$c6s->color->setRGB($colors[6]['r'], $colors[6]['g'], $colors[6]['b']);

$c7 = ms_newClassObj($rainfall);
$c7->setexpression("([DA] < ". $bins[7] .")");
$c7s = ms_newStyleObj($c7);
$c7s->color->setRGB($colors[7]['r'], $colors[7]['g'], $colors[7]['b']);

$c8 = ms_newClassObj($rainfall);
$c8->setexpression("([DA] < ". $bins[8] .")");
$c8s = ms_newStyleObj($c8);
$c8s->color->setRGB($colors[8]['r'], $colors[8]['g'], $colors[8]['b']);

$c9 = ms_newClassObj($rainfall);
$c9->setexpression("([DA] < ". $bins[9] .")");
$c9s = ms_newStyleObj($c9);
$c9s->color->setRGB($colors[9]['r'], $colors[9]['g'], $colors[9]['b']);

$c10 = ms_newClassObj($rainfall);
$c10->setexpression("([DA] < ". $bins[10] .")");
$c10s = ms_newStyleObj($c10);
$c10s->color->setRGB($colors[10]['r'], $colors[10]['g'], $colors[10]['b']);

$c11 = ms_newClassObj($rainfall);
$c11->setexpression("([DA] >= ". $bins[10] .")");
$c11s = ms_newStyleObj($c11);
$c11s->color->setRGB($colors[11]['r'], $colors[11]['g'], $colors[11]['b']);

$rainfall->draw($img);
} else {
  /* Draw something to say no values available */
  if ($map_width > 320) {
  $exp = $map->getlayerbyname("unavailable");
  $exp->set("status", MS_ON);
  $exp->draw($img);
  } else {
  $exp = $map->getlayerbyname("inprogress");
  $exp->set("status", MS_ON);
  $exp->draw($img);

  }
}

add_and_draw("counties");

//$dm = $map->getlayerbyname("dm");
//$dm->set("status", MS_ON);
//$dm->draw($img);

/* Need something to draw bars! */
$bar = $map->getlayerbyname("bar");

$layer = $map->getLayerByName("credits");
if ($map_width > 320)
{
$rt = ms_newRectObj();
$rt->setextent(0, 30, $map_width, 5);
$rt->draw($map, $bar, $img, 0, "");
$rt->free();
$point = ms_newpointobj();
$point->setXY(50, 20);
$point->draw($map, $layer, $img, 0, $param["title"]);
} else {
$rt = ms_newRectObj();
$rt->setextent(0, 20, $map_width, 5);
$rt->draw($map, $bar, $img, 0, "");
$rt->free();
$point = ms_newpointobj();
$point->setXY(5, 10);
$point->draw($map, $layer, $img, 1, $param["title"]);
}


$rt = ms_newRectObj();
$rt->setextent(0, $map_height, $map_width, $map_height - 20);
$rt->draw($map, $bar, $img, 0, "");
$rt->free();

if ($map_width > 320)
{
$rt = ms_newRectObj();
$rt->setextent(0, $map_height, 60, $map_height - 210);
$rt->draw($map, $bar, $img, 0, "");
$rt->free();
}

$point = ms_newpointobj();
$point->setXY(5, $map_height - 10);
$point->draw($map, $layer, $img, 1, "Map Units: ". $param["units"] ."  Iowa Daily Erosion Project         Map Generated on  ". date("Y/m/d"));

$layer = $map->getLayerByName("singlebox");
$x = 1;
$y = $map_height - 200;
$height = 14;
$width = 10;
for ($k=11;$k>=0;$k--){
 $p = ms_newRectObj();
 $p->setextent($x, $y + $height, $x + $width, $y);
 $cl = ms_newClassObj($layer);
 $st = ms_newStyleObj($cl);
 $st->color->setRGB($colors[$k]['r'], $colors[$k]['g'], $colors[$k]['b']);
 $st->outlinecolor->setRGB(255, 255, 255);
 $cl->label->color->setRGB(255, 255, 255);
 $cl->label->set("type", MS_BITMAP);
 $cl->label->set("size", MS_MEDIUM);
 $cl->label->set("position", MS_UR);
 $cl->label->set("offsetx", $width * 1.25);
 $cl->label->set("offsety", 0);
 $p->draw($map, $layer, $img, 11- $k, @$param["ramp"][$k]);
 $p->free();
 $y = $y + $height;
}


header("Content-type: image/png");
$img->saveImage('');
//$map->save('/tmp/t.map');
?>
