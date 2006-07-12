<?php
include("../../etc/config.inc.php");
/* Plot water balance goodies! */
$conn = pg_connect($weppdb);

/* Tunables */
$runid = isset($_GET["runid"]) ? intval($_GET["runid"]) : 166090;
$year = isset($_GET["year"]) ? intval($_GET["year"]) : date("Y");
//$myvar = isset($_GET["var"]) ? $_GET["var"] : "tsw";

$fcontents = file("/wepp/RT/wb/${runid}.wb");
$now = time();
$lbound = mktime(0,0,0,1,1,$year);
$obound = mktime(0,0,0,1,1,$year +1);
$now = time();

/* Need to figure out the soil depth */
$sql = "SELECT n.soil_depth from nri n, combos c WHERE c.id = $runid 
        and c.nri_id = n.id";
$rs = pg_exec($conn, $sql);
$row = pg_fetch_array($rs,0);
$soildepth = intval($row["soil_depth"]);

$params = Array(
 "tsw" => Array("title" => "Root Zone Soil Moisture", "column" => 5, 
    "factor" => $soildepth, "layer" => "top ". ($soildepth / 1000) ." m"),
 "s10cm" => Array("title" => "0 to 10cm Soil Moisture", "column" => 6,
    "factor" => 100, "layer" => "0-10 cm topsoil"),
 "s20cm" => Array("title" => "10 to 20cm Soil Moisture", "column" => 7,
    "factor" => 100, "layer" => "10-20 cm topsoil"),
);

$tsw = Array();
$t10sw = Array();
$t20sw = Array();
$dates = Array();

//$col = $params[$myvar]["column"];
//$factor = $params[$myvar]["factor"];
while (list ($line_num, $line) = each ($fcontents)) {
  if ($line_num < 14) { continue; }
  $parts = preg_split ("/[\s]+/", $line);
  $ts = mktime(0,0,0,1,1,1996 + $parts[3]) + (86400 * ($parts[2] - 1));
  if ($ts < $lbound || $ts >= $obound || $ts > $now) { continue; }
  //if ($parts[$col] == "NaN" || $parts[$col] == "******") { continue; }
  $dates[] = $ts;
  $tsw[] = $parts[5] / $soildepth * 100;
  $t10sw[] = $parts[6] / 100 * 100;
  $t20sw[] = $parts[7] / 100 * 100;
}

include ("$_BASE/include/jpgraph/jpgraph.php");
include ("$_BASE/include/jpgraph/jpgraph_line.php");
//include ("$_BASE/include/jpgraph/jpgraph_date.php");

$graph = new Graph(640,400);
$graph->SetScale("textlin",0, 50);
$graph->SetFrame(false);
$graph->SetTickDensity(TICKD_SPARSE);

$graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCFF@0.5');

$graph->img->SetMargin(50,10,60,50);

$graph->tabtitle->Set("WEPP Modelled Soil Moisture");
$graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);

$graph->subtitle->Set("Values shown for runid $runid during $year");

$graph->yaxis->SetTitle("Volumetric Soil Moisture [%] ");
$graph->xaxis->SetLabelAngle(90); 
$graph->yaxis->HideZeroLabel();

function  DateCallback( $aVal) {
    global $lbound;
    $ts = $lbound + ($aVal * 86400);
    if (Date ('d',$ts) == "01")
      return Date ('M d',$ts);
    return "";
}
//$graph->xaxis->scale-> SetDateAlign( MONTHADJ_1);
//$graph->xaxis->SetTickLabels($dates);
$graph->xaxis-> SetLabelFormatCallback( 'DateCallback'); 

$lineplot=new LinePlot($tsw);
$lineplot->SetColor("red");
$lineplot->SetLegend("0-". intval($soildepth/10) ."cm layer");
$lineplot->SetWeight(2);

$lineplot2=new LinePlot($t10sw);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("0-10cm layer");
$lineplot2->SetWeight(2);

$lineplot3=new LinePlot($t20sw);
$lineplot3->SetColor("green");
$lineplot3->SetLegend("10-20cm layer");
$lineplot3->SetWeight(2);

$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->Add($lineplot3);

$graph->legend->SetPos(0.01,0.01);

// Display the graph
$graph->Stroke();


?>
