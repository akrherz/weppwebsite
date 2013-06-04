<?php
/* weppmap.inc.php 
   - Need something to make GIS plots.  More OO, the better!
*/

dl("php_mapscript_401.so");

class weppmap
{

function weppmap()
{
	$this->map =  ms_newMapObj("$_BASE/data/gis/map/wepp.map");

} // End of constructor weppmap()




} // End of weppmap
?>
