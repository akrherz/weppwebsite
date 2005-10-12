<?php
// An example plot to show at the WEPP meeting
$ts = isset($_GET["ts"]) ? $_GET["ts"] : "2003-05-04";

$c = pg_connect("10.10.10.20","5432","wepp");
$q = "SELECT runoff / 25.4 as runoff, loss * 4.463 as loss from results WHERE valid = '$ts' LIMIT 1000";
$rs = pg_exec($c, $q);
pg_close($c);

$runoff = Array();
$loss = Array();

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++){
  $runoff[$i] = $row["runoff"];
  $loss[$i] = $row["loss"];
} 

include("jpgraph/jpgraph.php");
include("jpgraph/jpgraph_scatter.php");

$graph = new Graph(640,480,"example1");
$graph->SetScale("lin");
$graph->img->SetMargin(40,10,35,50);

$graph->title->Set("Loss vs Runoff for $ts");
$graph->xaxis->SetTitle("Soil Loss [t/a]");
$graph->yaxis->SetTitle("Runoff [inches]");


$sp=new ScatterPlot($runoff, $loss);
$sp->mark->SetWidth(4);
$sp->mark->SetType(MARK_FILLEDCIRCLE);
$sp->mark->SetFillColor("navy");

$graph->Add($sp);

$graph->Stroke();
?>
