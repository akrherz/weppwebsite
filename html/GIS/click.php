<?php
// Hack to figure out where we clicked?
include("../../etc/config.inc.php");

$dstr = isset($_GET["dstr"]) ? $_GET["dstr"]: "";
$cgiStr = "1=1";
$map_x = $_GET["img_x"];
$map_y = $_GET["img_y"];
$map_height = $_GET["map_height"];
$map_width = $_GET["map_width"];
$ul_x = $_GET["ul_x"];
$ul_y = $_GET["ul_y"];
$lr_x = $_GET["lr_x"];
$lr_y = $_GET["lr_y"];
if (isset($_GET["year"])) $cgiStr .= "&year=". $_GET["year"] ;
if (isset($_GET["month"])) $cgiStr .= "&month=". $_GET["month"] ;
if (isset($_GET["day"])) $cgiStr .= "&day=". $_GET["day"] ;

$dx = ($ul_x - $lr_x) / $map_width;
$dy = ($ul_y - $lr_y) / $map_height;


$clickx = ($map_x * (0 - $dx) ) + $ul_x;
$clicky = ($map_y * (0 - $dy) ) + $ul_y;

$c = pg_connect("host=iemdb port=5432 dbname=wepp user=nobody");
$q = "select * from iatwp WHERE within(geometryfromtext('POINT($clickx $clicky)', 26915), the_geom)";
$rs = pg_exec($c, $q);

$row = @pg_fetch_array($rs, 0);

$twp = $row["model_twp"];

if (strlen($twp) == 0) die("You did not click in Iowa! $clickx $clicky");

header("Location: $_WEBBASE/township/byday.phtml?twp=$twp&$cgiStr&dstr=$dstr");

?>
