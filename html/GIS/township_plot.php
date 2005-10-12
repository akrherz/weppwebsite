<?php
include("../../etc/config.inc.php");
$twp = $_GET['twp'];
$size = isset($_GET["size"]) ? $_GET["size"] : "600x600";
$wmslayer = isset($_GET["wmslayer"]) ? $_GET["wmslayer"] : "doqqs";
$szr = explode("x", $size);
$width = $szr[0];
$height = $szr[1];

// Something to generate Mapserver township Stuff
$c = pg_connect($weppdb);
$q = "SELECT xmin(extent) as x0, xmax(extent) as x1,
             ymin(extent) as y0, ymax(extent) as y1 FROM 
        (select extent(the_geom) as extent from iatwp 
         WHERE model_twp = '$twp') as foo";
$rs = pg_exec($c, $q);
$row = pg_fetch_array($rs,0);


dl($mapscript);
$map = ms_newMapObj("$_BASE/data/gis/map/wepp.map");
$map->set("height", $height);
$map->set("width", $width);
$map->selectoutputformat("PNG24");
$map->setextent($row["x0"] - 1000, $row["y0"] - 1000, $row["x1"] + 1000, $row["y1"] + 1000);

$ll = $map->getlayerbyname("wmsback");
$ll->set("status", MS_ON);
$ll->set("connection", "http://cairo.gis.iastate.edu/cgi-bin/server.cgi?format=jpeg&wmtver=1.0.0&request=map&servicename=GetMap&layers=". $wmslayer);


$img = $map->prepareImage();

$ll->draw($img);

$rect = $map->getlayerbyname("rect");
$rect->set("status", MS_ON);

$rt = ms_newRectObj();
$rt->setextent($row["x0"], $row["y0"], $row["x1"], $row["y1"]);
$rt->draw($map, $rect, $img, 0, $twp);
$rt->free();

$map->drawLabelCache($img);


$url = $img->saveWebImage(MS_PNG, 0,0,-1);

include("$_BASE/include/header.phtml");
?>
<!-- content BEGIN -->
<div id="wepp-middle-one">
<div id="wepp-content">
<div id="page-main">

<form method="get" action="township_plot.php" name="myform">
<div class="table">
<table>
<thead><tr><th>Township:</th><th>Select Layer:</th><th>Image Size</th><th></th></tr></thead>
<tbody><tr>
<td>
 <input type="text" size="12" name="twp" value="<?php echo $twp; ?>">
</td>
<td>
<select name="wmslayer">
 <option value="doqqs" <?php if ($wmslayer == "doqqs") echo "SELECTED"; ?>>Digital Ortho Quads
 <option value="drg100" <?php if ($wmslayer == "drg100") echo "SELECTED"; ?>>1:100k Topographic
 <option value="cir" <?php if ($wmslayer == "cir") echo "SELECTED"; ?>>Color Infrared
 <option value="ortho_bw_2002" <?php if ($wmslayer == "ortho_bw_2002") echo "SELECTED"; ?>>Color IR (Grayscale)
</select>
</td>
<td>
<select name="size">
 <option value="400x400" <?php if ($size == "400x400") echo "SELECTED"; ?>>400x400
 <option value="600x600" <?php if ($size == "600x600") echo "SELECTED"; ?>>600x600
 <option value="800x800" <?php if ($size == "800x800") echo "SELECTED"; ?>>800x800
</select>
</td>
<td><input type="submit" value="Make Map"></td>
</tr></tbody></table></div>


<img src="<?php echo $url; ?>" border="1">

<p><i>Right click on the image to save it!</i>

</div></div></div>

<?php include("$_BASE/include/footer.phtml"); ?>

