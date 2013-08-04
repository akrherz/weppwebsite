<?php
include("../../etc/config.inc.php");
/* Plot water balance goodies! */
$conn = pg_connect($weppdb);
/* Tunables */
$runid = isset($_GET["runid"]) ? intval($_GET["runid"]) : 166090;
$year = isset($_GET["year"]) ? intval($_GET["year"]) : date("Y");

/* Queries */
$rs = pg_prepare($conn, "metadata", "SELECT t.county as cname, c.hrap_i, s.name as soil_name, m.name as man_name, c.model_twp, n.soil_depth from nri n, combos c, managements m, soils s, iatwp t WHERE c.id = $1 and c.nri_id = n.id and n.man_id = m.man_id and n.soil_id = s.soil_id and c.model_twp = t.model_twp");
$rs = pg_prepare($conn, "rainfall", "SELECT valid, rainfall / 25.4 as ra from daily_rainfall_$year WHERE hrap_i = $1 ORDER by valid ASC");


$fcontents = file("/mnt/idep/RT/wb/${runid}.wb");
$now = time();
$lbound = mktime(0,0,0,1,1,$year);
$obound = mktime(0,0,0,1,1,$year +1);
$now = time();

/* Need to figure out the soil depth */
$rs = pg_execute($conn, "metadata", Array($runid) );
$row = pg_fetch_array($rs,0);
$soildepth = intval($row["soil_depth"]);
$modeltwp = $row["model_twp"];
$management = $row["man_name"];
$soilname = $row["soil_name"];
$hrapi = $row["hrap_i"];
$cname = $row["cname"];

$rs = pg_execute($conn, "rainfall", Array($hrapi) );
$row = pg_fetch_array($rs,0);
$rainfall = Array();
$rdates = Array();
$total_rainfall = 0;
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $rdates[] = strtotime($row["valid"]);
  $rainfall[] = $row["ra"];
  $total_rainfall += $row["ra"];
}

$params = Array(
 "tsw" => Array("title" => "Root Zone Soil Moisture", "column" => 5, 
    "factor" => $soildepth, "layer" => "top ". ($soildepth / 1000) ." m"),
 "s10cm" => Array("title" => "0 to 10cm Soil Moisture", "column" => 6,
    "factor" => 100, "layer" => "0-10 cm topsoil"),
 "s20cm" => Array("title" => "10 to 20cm Soil Moisture", "column" => 7,
    "factor" => 100, "layer" => "10-20 cm topsoil"),
);

$tsw = Array();
$et = Array();
$t10sw = Array();
$t20sw = Array();
$dates = Array();

while (list ($line_num, $line) = each ($fcontents)) {
  if ($line_num < 20) { continue; }
  $parts = preg_split ("/[\s]+/", $line);
  //print_r($parts);
  $ts = mktime(0,0,0,1,1, $parts[3]) + (86400 * $parts[2]);
  if ($ts < $lbound || $ts >= $obound || $ts > $now) { continue; }
  //if ($parts[$col] == "NaN" || $parts[$col] == "******") { continue; }
  $dates[] = $ts;
  $tsw[] = $parts[5] / $soildepth * 100;
  $t10sw[] = $parts[6] / 100 * 100;
  $t20sw[] = $parts[7] / 100 * 100;
  $et[] = floatval($parts[8]);
}

include ("$_BASE/include/jpgraph/jpgraph.php");
include ("$_BASE/include/jpgraph/jpgraph_line.php");
include ("$_BASE/include/jpgraph/jpgraph_bar.php");
include ("$_BASE/include/jpgraph/jpgraph_date.php");

$graph = new Graph(800,600);
$graph->SetScale("datlin",0, 50);
$graph->SetY2Scale('lin', 0, max( Array(intval(max($et))+1,10) ) );
$graph->SetFrame(false);
$graph->SetTickDensity(TICKD_SPARSE);

$graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCFF@0.5');

$graph->img->SetMargin(50,50,60,50);

$graph->tabtitle->Set("WEPP Modelled Soil Moisture");
$graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);

//$graph->subtitle->Set("Values shown for runid $runid during $year");

$graph->yaxis->SetTitle("Volumetric Soil Moisture [%] ");
$graph->y2axis->SetTitle("Rainfall (bars) [inch] and Plant ET (green) [mm]");
$graph->xaxis->SetLabelAngle(90); 
$graph->yaxis->HideZeroLabel();

function  DateCallback( $aVal) {
    //global $lbound;
    //$ts = $lbound + ($aVal * 86400);
    //if (Date ('d',$ts) == "01")
      return Date ('M d',$aVal);
    //return "";
}
$graph->xaxis->scale-> SetDateAlign( MONTHADJ_1);
//$graph->xaxis->SetTickLabels($dates);
//$graph->xaxis-> SetLabelFormatCallback( 'DateCallback'); 
$graph->xaxis->scale->SetDateFormat( 'M d');
$graph->xaxis->SetTickSide(SIDE_DOWN);

$lineplot=new LinePlot($tsw, $dates);
$lineplot->SetColor("tan");
$lineplot->SetLegend("0-". intval($soildepth/10) ."cm layer");
$lineplot->SetWeight(2);

$lineplot2=new LinePlot($t10sw, $dates);
$lineplot2->SetColor("blue");
$lineplot2->SetLegend("0-10cm layer");
$lineplot2->SetWeight(2);

$lineplot3=new LinePlot($t20sw, $dates);
$lineplot3->SetColor("red");
$lineplot3->SetLegend("10-20cm layer");
$lineplot3->SetWeight(2);

$graph->Add($lineplot);
$graph->Add($lineplot2);
$graph->Add($lineplot3);

$lineplot4=new LinePlot($et, $dates);
$lineplot4->SetColor("green");
$lineplot4->SetLegend("Plant ET");
$lineplot4->SetWeight(2);
$graph->AddY2($lineplot4);


$bp=new BarPlot($rainfall, $rdates);
$bp->SetColor("black");
//$bp->SetLegend("10-20cm layer");
//$bp->SetWeight(2);
$graph->AddY2($bp);


$graph->legend->SetPos(0.1,0.01);

$tx1 = new Text("Township: $modeltwp  Management: $management  Soil: $soilname Total Rainfall: ". round($total_rainfall,2) ." in
IDEP Run ID: $runid   Year: $year   Iowa County: $cname");
$tx1->SetPos(0.02,0.00, 'left', 'top');
$tx1->SetFont(FF_FONT1, FS_BOLD, 16);
$graph->Add($tx1);

// Display the graph
$graph->Stroke();
?>
