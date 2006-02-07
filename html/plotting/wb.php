<?php
include("../../etc/config.inc.php");
/* Plot water balance goodies! */

$fcontents = file("166090.wb");
$now = time();
$lbound = mktime(0,0,0,1,1,2002);
$obound = mktime(0,0,0,1,1,2003);

$tsw = Array();
$dates = Array();

while (list ($line_num, $line) = each ($fcontents)) {
  if ($line_num < 14) { continue; }
  $parts = preg_split ("/[\s]+/", $line);
  $ts = mktime(0,0,0,1,1,1996 + $parts[3]) + (86400 * $parts[2]);
  if ($ts < $lbound || $ts >= $obound) { continue; }
  if ($parts[12] == "NaN" || $parts[12] == "******") { continue; }
  $dates[] = $ts;
  $tsw[] = $parts[12];
}

include ("$_BASE/include/jpgraph/jpgraph.php");
include ("$_BASE/include/jpgraph/jpgraph_line.php");
include ("$_BASE/include/jpgraph/jpgraph_date.php");

$graph = new Graph(640,400,"example1");
$graph->SetScale("datlin");

$graph->xaxis->SetLabelAngle(90); 
//$graph->xaxis->scale->SetDateAlign(MONTHADJ_1);

$lineplot=new LinePlot($tsw, $dates);
$lineplot->SetLegend("BA");
$lineplot->SetColor("red");

$graph->Add($lineplot);

// Display the graph
$graph->Stroke();


?>
