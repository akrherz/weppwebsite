<?php include("../etc/config.inc.php"); ?>
<html>
<head>
 <link type="text/css" href="css/ui-lightness/jquery-ui-1.8.22.custom.css" rel="stylesheet" />
 <script type="text/javascript" src="js/jquery-1.7.2.min.js"></script>
 <script type="text/javascript" src="js/jquery-ui-1.8.22.custom.min.js"></script>
 <script src='js/OpenLayers.js'></script>
 <link rel='stylesheet' 
  href='css/default/style.css' type='text/css'>
          <style type="text/css">
     .dp {
     border: 0px;
background: black;
color: white;
font-weight: bolder;
font-size: 1.3em;
width: 149px;
float: left;
     }
            html, body, #map {
                margin: 0;
                width: 100%;
                height: 100%;
            }
            #detailsContainer {
                position: absolute;
                bottom: 1em;
                right: 1em;
                width: 200px;
                z-index: 20001;
                background-color: #53675A;
                padding: 0.1em;
            }
            #details {
                background-color: #FFF;
                padding: 0.1em;
            }
            #controller {
                position: absolute;
                bottom: 0.5em;
                left: 0.5em;
                padding-right: 0.5em;
                background-color: #000;
                z-index: 20001;
                padding-left: 0.5em;
            }
            #ramp {
                position: absolute;
                bottom: 50px;
                left: 0.5em;
                background-color: #000;
                z-index: 20000;
                padding-left: 0.5em;
            }
			#quick {
				position: absolute;
				top: 0px;
				left: 50px;
				z-index: 20000;
			}
			#quick ul {
				float: right;
				list-style-type: none;
				padding: 0;
				margin: 0;
				margin-right: -2px;
			}
			#quick li {
				float: left;
				margin: 0;
				border: 1px solid #999;
				padding: 6px 8px 3px 8px;
				margin-left: -1px;
				background: white;
			}
        </style>
        <script type="text/javascript">
var tilecache = "<?php echo TILECACHE; ?>";
        </script>
 <script src='nextgen.js'></script>
</head>
<body onload="init()">
<div id="quick">
<ul>
	<li><a href="javascript: selectEvent(1);">May6, 07</a></li>
	<li><a href="javascript: selectEvent(2);">May24, 04</a></li>
	<li><a href="javascript: selectEvent(3);">Sep14, 04</a></li>
	<li><a href="javascript: selectEvent(4);">Aug25, 12</a></li>
	<li><a href="javascript: selectEvent(5);">Aug26, 12</a></li>
</ul>
</div>
<div id="detailsContainer">
	<div id="details">
		<div id="details_loading"><img src="images/wait24trans.gif" /> Loading...</div>
		<div id="details_details"></div>
	</div>
</div>
<div id="controller">
	<form>
	<input type="text" name="date" id="datepicker" class="dp" />
	<span style="font-size: 1.3em; color:#FFF; font-weight:bolder;">Iowa Daily Erosion Project</span>
	<br clear="both"/>&nbsp;<br />
	<div id="radio">
		<input type="radio" id="loss_opt" name="radio" value="loss" /><label for="loss_opt">Erosion</label>
		<input type="radio" id="precip-in_opt" name="radio" value="precip-in" /><label for="precip-in_opt">Precipitation</label>
		<input type="radio" id="runoff_opt" name="radio" value="runoff" /><label for="runoff_opt">Runoff</label>
		<input type="radio" id="vsm_opt" name="radio" value="vsm" checked="checked" /><label for="vsm_opt">Soil Moisture</label>
	</form>
	</div>
</div>
<div id="ramp">
<img src="images/vsm-ramp.png" id="rampimg" />
<br /> &nbsp; 
<br /> &nbsp; 
<br /> &nbsp; 
<br /> &nbsp; 
</div>
<div id="map"></div>
</body>
</html>