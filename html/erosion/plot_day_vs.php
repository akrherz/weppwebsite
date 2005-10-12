<?php
// An example plot to show at the WEPP meeting
$ts = isset($_GET["ts"]) ? $_GET["ts"] : "2003-05-04";

$c = pg_connect("db1.mesonet.agron.iastate.edu","5432","wepp");
//$q = "select * from results WHERE valid = '2003-05-04'";
$q = "select r.*, n.steep from results r, combos c, nri n WHERE r.valid = '2003-05-04' and  r.run_id = c.id and c.nri_id = n.id";
$rs = pg_exec($c, $q);

$runoff0 = Array();
$loss0 = Array();
$precip0 = Array();

$runoff1 = Array();
$loss1 = Array();
$precip1 = Array();

$runoff2 = Array();
$loss2 = Array();
$precip2 = Array();

$runoff3 = Array();
$loss3 = Array();
$precip3 = Array();

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++){
  $s = intval($row["steep"]);
	if ($s < 5) {
		$runoff0[] = $row["runoff"];
		$loss0[] = $row["loss"];
		$precip0[] = $row["precip"] / 25.4;
	} elseif ($s < 10){
		$runoff1[] = $row["runoff"];
		$loss1[] = $row["loss"];
		$precip1[] = $row["precip"] / 25.4;
	} elseif ($s < 15){
		$runoff2[] = $row["runoff"];
		$loss2[] = $row["loss"];
		$precip2[] = $row["precip"] / 25.4;
	} else{
		$runoff3[] = $row["runoff"];
		$loss3[] = $row["loss"];
		$precip3[] = $row["precip"] / 25.4;
	} 
} 

include("../../include/jpgraph/jpgraph.php");
include("../../include/jpgraph/jpgraph_scatter.php");

$graph = new Graph(640,480,"example1");
$graph->SetScale("lin");
$graph->img->SetMargin(40,10,35,50);

$graph->title->Set("Loss ($tloss) vs Distance for $ts ");
$graph->xaxis->SetTitle("Distance [kilometers]");
$graph->yaxis->SetTitle("Max Loss [ton/acre]");
$graph ->xaxis->SetPos( "min");

$sp0=new ScatterPlot($runoff0, $precip0);
$sp0->SetLegend("< 5%");
$sp0->mark->SetWidth(4);
$sp0->mark->SetType(MARK_FILLEDCIRCLE);
$sp0->mark->SetFillColor("green");

$sp1=new ScatterPlot($runoff1, $precip1);
$sp1->SetLegend("5 < 10%");
$sp1->mark->SetWidth(4);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("navy");

$sp2=new ScatterPlot($runoff2, $precip2);
$sp2->SetLegend("10 < 15%");
$sp2->mark->SetWidth(4);
$sp2->mark->SetType(MARK_FILLEDCIRCLE);
$sp2->mark->SetFillColor("yellow");

$sp3=new ScatterPlot($runoff3, $precip3);
$sp3->SetLegend(">= 15%");
$sp3->mark->SetWidth(4);
$sp3->mark->SetType(MARK_FILLEDCIRCLE);
$sp3->mark->SetFillColor("red");

$graph->Add($sp0);
$graph->Add($sp1);
$graph->Add($sp2);
$graph->Add($sp3);

$graph->Stroke();
?>
