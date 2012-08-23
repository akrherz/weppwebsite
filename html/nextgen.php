<?php include("../etc/config.inc.php"); ?>
<html>
<head>
 <link type="text/css" href="css/ui-lightness/jquery-ui-1.8.22.custom.css" rel="stylesheet" />
 <script type="text/javascript" src="js/jquery-1.7.2.min.js"></script>
 <script type="text/javascript" src="js/jquery-ui-1.8.22.custom.min.js"></script>
 <script src='http://openlayers.org/api/2.12/OpenLayers.js'></script>
 <link rel='stylesheet' 
  href='http://openlayers.org/api/2.12/theme/default/style.css' type='text/css'>
          <style type="text/css">
            html, body, #map {
                margin: 0;
                width: 100%;
                height: 100%;
            }
            #title {
                position: absolute;
                top: 1em;
                left: 4em;
                z-index: 20001;
                color: #fff;
                background-color: #000;
				filter: alpha(opacity=50, style=0);
				-moz-opacity: 50%; 
                padding: 0.1em;
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
                bottom: 1em;
                left: 1em;
                
                z-index: 20000;
                background-color: #53675A;
                padding: 0.1em;
            }

        </style>
 <script src='nextgen.js'></script>
</head>
<body onload="init()">
<div id="title">
   <p>This is my title!</p>
</div>
<div id="detailsContainer">
	<div id="details">
		<p>Location Details!</p>
	</div>
</div>
<div id="controller">
	<form>
	<input type="text" name="date" id="datepicker" />

	<div id="radio">
		<input type="radio" id="radio1" name="radio" value="vsm" checked="checked" /><label for="radio1">Root Zone Soil Moisture</label>
		<input type="radio" id="radio2" name="radio" value="precip-in" /><label for="radio2">Precipitation</label>
		<input type="radio" id="radio3" name="radio" value="runoff" /><label for="radio3">Runoff</label>
	</form>
	</div>
	
</div>
	<div id="map"></div>
</body>
</html>