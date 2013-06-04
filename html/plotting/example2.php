<?php
// An example plot to show at the WEPP meeting
$ts = isset($_GET["ts"]) ? $_GET["ts"] : "2003-05-04";
$twp = isset($_GET["twp"]) ? $_GET["twp"] : "T81NR40W";

$c = pg_connect("10.10.10.20","5432","wepp");
$q = "select r.*, t.the_geom from results_by_twp r, iatwp t 
   WHERE r.valid = '2003-05-04' and r.model_twp = '$twp' 
   and r.model_twp = t.model_twp";
$rs = pg_exec($c, $q);

$row = pg_fetch_array($rs,0);
$geom = $row["the_geom"];
$myloss = $row["max_loss"];
$tloss = round(floatval($myloss) * 4.463, 2);

$q = "SELECT distance('$geom', t.the_geom) / 1000.00 as distance, 
  ($myloss - r.max_loss) * 4.463 as diff from 
  iatwp t, results_by_twp r WHERE r.valid = '2003-05-04' and 
  r.model_twp = t.model_twp";
$rs = pg_exec($c, $q);


pg_close($c);

$distance = Array();
$loss = Array();

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++){
  $distance[$i] = $row["distance"];
  $loss[$i] = $row["diff"];
} 

include("jpgraph/jpgraph.php");
include("jpgraph/jpgraph_scatter.php");

$graph = new Graph(640,480,"example1");
$graph->SetScale("lin");
$graph->img->SetMargin(40,10,35,50);

$graph->title->Set("Loss ($tloss) vs Distance for $ts for $twp");
$graph->xaxis->SetTitle("Distance [kilometers]");
$graph->yaxis->SetTitle("Max Loss [ton/acre]");
 $graph ->xaxis->SetPos( "min");

$sp=new ScatterPlot($loss, $distance);
$sp->mark->SetWidth(4);
$sp->mark->SetType(MARK_FILLEDCIRCLE);
$sp->mark->SetFillColor("navy");

$graph->Add($sp);

$graph->Stroke();
?>
