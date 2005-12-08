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

/* Dictionaries */
$c = Array();
$c[0] = Array('r'=>  0,'g'=> 236,'b'=> 236); // 
$c[1] = Array('r'=>  1,'g'=> 160,'b'=> 246); // 
$c[2] = Array('r'=>  0,'g'=>   0,'b'=> 246); // 
$c[3] = Array('r'=>  0,'g'=> 255,'b'=>   0); // 
$c[4] = Array('r'=>  0,'g'=> 200,'b'=>   0); // 
$c[5] = Array('r'=>  0,'g'=> 144,'b'=>   0); // 
$c[6] = Array('r'=>255,'g'=> 255,'b'=>   0); // 
$c[7] = Array('r'=>231,'g'=> 192,'b'=>   0); // 
$c[8] = Array('r'=>255,'g'=> 144,'b'=>   0); // 
$c[9] = Array('r'=>255,'g'=>   0,'b'=>   0); // 
$c[10] = Array('r'=>214,'g'=>  0,'b'=>   0); // 
$c[11] = Array('r'=>192,'g'=>  0,'b'=>   0); // 


$ramps = Array(
	0 =>  Array(0.1, 0.25, 0.5, 1, 2, 3, 4, 5),
	1 => Array(0.5, 1, 2, 3, 4, 6, 8, 10),
	2 => Array(1, 2, 4, 6, 9, 12, 16, 23),               // Precip(hours)
	3 => Array(2, 4, 8, 16, 24, 32, 64, 128),            // Precip(mm)
	4 => Array(4, 8, 12, 16, 20, 25, 30, 35),
	5 => Array(5, 10, 20, 40, 60, 100, 120, 160),
	6 => Array(10, 25, 50, 75, 100, 150, 200, 250),
	7 => Array(100, 200, 300, 400, 500, 600, 800, 1000),
	8 => Array(0.1, 0.25, 0.5, 1, 1.5, 2, 3, 5)           // Precip(in)
);
$mo_ramps = Array(
	0 =>  Array(0.1, 0.5, 1, 2, 4, 8, 16, 24),
	1 => Array(0.5, 1, 2, 3, 4, 6, 8, 10),
	2 => Array(1, 2, 4, 6, 8, 10, 12, 20),
	3 => Array(10, 25, 50, 75, 100, 150, 200, 250),
	4 => Array(4, 8, 12, 16, 20, 25, 30, 35),
	5 => Array(5, 10, 20, 40, 60, 100, 120, 160),
	6 => Array(10, 25, 50, 75, 100, 150, 200, 250),
	7 => Array(100, 200, 300, 400, 500, 600, 800, 1000),
	8 => Array(0.1, 0.5, 1, 2, 3, 5, 7, 10)
);

$yr_ramps = Array(
	0 =>  Array(0.1, 0.5, 1, 2, 4, 8, 16, 24),
	1 => Array(0.5, 1, 2, 3, 4, 6, 8, 10),
	2 => Array(1, 2, 4, 6, 8, 10, 12, 20),
	3 => Array(100, 200, 300, 400, 500, 750, 1000, 1250),
	4 => Array(4, 8, 12, 16, 20, 25, 30, 35),
	5 => Array(5, 10, 20, 40, 60, 100, 120, 160),
	6 => Array(10, 25, 50, 75, 100, 150, 200, 250),
	7 => Array(100, 200, 300, 400, 500, 600, 800, 1000),
	8 => Array(1, 2, 6, 10, 14, 18, 22, 26)
);

$params = Array(
"rainfall_in" => Array('dbstr' => 'rainfall / 25.4',
  'units' => 'inches', 
  'title' => "Estimated Rainfall on ",
  'table' => "daily_rainfall_$year", 'myramp' => 8,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"rainfall_mm" => Array('dbstr' => 'rainfall',
  'units' => 'millimeters', 
  'title' => "Estimated Rainfall on ",
  'table' => "daily_rainfall_$year", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"peak_15min_in" => Array('dbstr' => '(peak_15min / 25.4) * 4.0',
  'units' => 'inches per hour', 
  'title' => "Peak Rainfall Intensity on ",
  'table' => "daily_rainfall_$year", 'myramp' => 8,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"peak_15min_mm" => Array('dbstr' => '(peak_15min) * 4.0',
  'units' => 'millimeters per hour', 
  'title' => "Peak Rainfall Intensity on ",
  'table' => "daily_rainfall_$year", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"time_" => Array('dbstr' => '(hr_cnt) / 4.0',
  'units' => 'hours', 
  'title' => "Rainfall Duration: ",
  'table' => "daily_rainfall_$year", 'myramp' => 2,
  'maplayer' => 'daily_rainfall', 'gtype' => 'hrap',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"min_runoff_in" => Array('dbstr' => 'min_runoff / 25.4',
  'units' => 'inches', 
  'title' => "Minimum Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"avg_runoff_in" => Array('dbstr' => 'avg_runoff / 25.4',
  'units' => 'inches', 
  'title' => "Average Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"max_runoff_in" => Array('dbstr' => 'max_runoff / 25.4',
  'units' => 'inches', 
  'title' => "Maximum Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"min_runoff_mm" => Array('dbstr' => 'min_runoff',
  'units' => 'millimeters', 
  'title' => "Minimum Runoff: ",
  'table' => "results_by_twp", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"avg_runoff_mm" => Array('dbstr' => 'avg_runoff',
  'units' => 'millimeters', 
  'title' => "Average Runoff: ",
  'table' => "results_by_twp", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"max_runoff_mm" => Array('dbstr' => 'max_runoff',
  'units' => 'millimeters', 
  'title' => "Maximum Runoff: ",
  'table' => "results_by_twp", 'myramp' => 3,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"min_loss_acre" => Array('dbstr' => 'min_loss * 4.463',
  'units' => 'tons per acre', 
  'title' => "Minimum Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"avg_loss_acre" => Array('dbstr' => 'avg_loss * 4.463',
  'units' => 'tons per acre', 
  'title' => "Average Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"max_loss_acre" => Array('dbstr' => 'max_loss * 4.463',
  'units' => 'tons per acre', 
  'title' => "Maximum Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"min_loss_hectre" => Array('dbstr' => 'min_loss * 10.0',
  'units' => 'tons per hectre', 
  'title' => "Minimum Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"avg_loss_hectre" => Array('dbstr' => 'avg_loss * 10.0',
  'units' => 'tons per hectre', 
  'title' => "Average Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"max_loss_hectre" => Array('dbstr' => 'max_loss * 10.0',
  'units' => 'tons per hectre', 
  'title' => "Maximum Soil Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"ve_runoff_in" => Array('dbstr' => 've_runoff / 25.4',
  'units' => 'inches', 
  'title' => "Variance Estimator for Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"ve_runoff_mm" => Array('dbstr' => 've_runoff',
  'units' => 'millimeters', 
  'title' => "Variance Estimator for Runoff: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"ve_loss_acre" => Array('dbstr' => 've_loss * 4.463',
  'units' => 'tons per acre', 
  'title' => "Variance Estimator for Loss: ",
  'table' => "results_by_twp", 'myramp' => 0,
  'maplayer' => 'daily_rainfall', 'gtype' => 'twp',
  'dbdate' => strftime("%Y-%m-%d", $ts) ),

"ve_loss_hectre" => Array('dbstr' => 've_loss * 10.0',
  'units' => 'tons per hectre', 
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
$rainfall->set("data", $sql);

$bins = $param["ramp"];

$cz = ms_newClassObj($rainfall);
$cz->setexpression("([DA] == 0)");

$c0 = ms_newClassObj($rainfall);
$c0->setexpression("([DA] < ". $bins[0] .")");
$c0s = ms_newStyleObj($c0);
$c0s->color->setRGB($c[0]['r'], $c[0]['g'], $c[0]['b']);

$c1 = ms_newClassObj($rainfall);
$c1->setexpression("([DA] < ". $bins[1] .")");
$c1s = ms_newStyleObj($c1);
$c1s->color->setRGB($c[1]['r'], $c[1]['g'], $c[1]['b']);

$c2 = ms_newClassObj($rainfall);
$c2->setexpression("([DA] < ". $bins[2] .")");
$c2s = ms_newStyleObj($c2);
$c2s->color->setRGB($c[2]['r'], $c[2]['g'], $c[2]['b']);

$c3 = ms_newClassObj($rainfall);
$c3->setexpression("([DA] < ". $bins[3] .")");
$c3s = ms_newStyleObj($c3);
$c3s->color->setRGB($c[3]['r'], $c[3]['g'], $c[3]['b']);

$c4 = ms_newClassObj($rainfall);
$c4->setexpression("([DA] < ". $bins[4] .")");
$c4s = ms_newStyleObj($c4);
$c4s->color->setRGB($c[4]['r'], $c[4]['g'], $c[4]['b']);

$c5 = ms_newClassObj($rainfall);
$c5->setexpression("([DA] < ". $bins[5] .")");
$c5s = ms_newStyleObj($c5);
$c5s->color->setRGB($c[5]['r'], $c[5]['g'], $c[5]['b']);

$c6 = ms_newClassObj($rainfall);
$c6->setexpression("([DA] < ". $bins[6] .")");
$c6s = ms_newStyleObj($c6);
$c6s->color->setRGB($c[6]['r'], $c[6]['g'], $c[6]['b']);

$c7 = ms_newClassObj($rainfall);
$c7->setexpression("([DA] < ". $bins[7] .")");
$c7s = ms_newStyleObj($c7);
$c7s->color->setRGB($c[7]['r'], $c[7]['g'], $c[7]['b']);

$c8 = ms_newClassObj($rainfall);
$c8->setexpression("([DA] >= ". $bins[7] .")");
$c8s = ms_newStyleObj($c8);
$c8s->color->setRGB($c[8]['r'], $c[8]['g'], $c[8]['b']);

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
$height = 20;
$width = 10;
for ($k=8;$k>=0;$k--){
 $p = ms_newRectObj();
 $p->setextent($x, $y + $height, $x + $width, $y);
 $cl = ms_newClassObj($layer);
 $st = ms_newStyleObj($cl);
 $st->color->setRGB($c[$k]['r'], $c[$k]['g'], $c[$k]['b']);
 $st->outlinecolor->setRGB(255, 255, 255);
 $cl->label->color->setRGB(255, 255, 255);
 $cl->label->set("type", MS_BITMAP);
 $cl->label->set("size", MS_MEDIUM);
 $cl->label->set("position", MS_UR);
 $cl->label->set("offsetx", $width * 1.25);
 $cl->label->set("offsety", 0);
 $p->draw($map, $layer, $img, 8- $k, @$param["ramp"][$k]);
 $p->free();
 $y = $y + $height;
}


header("Content-type: image/png");
$img->saveImage('');
?>
