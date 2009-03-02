<?php
  include("../../etc/config.inc.php");
  include("$_BASE/include/forms.php");
  $pgconn = pg_connect($weppdb);

$rs = pg_prepare($pgconn, "COMBOS", "select c.id as combo_id, n.len as len, 
      m.name as man_name, 
      n.steep as steep, c.hrap_i as hrap_i
      from combos c, nri n, managements m WHERE n.man_id = m.man_id and 
      n.id = c.nri_id and n.model_twp = c.model_twp and n.model_twp = $1
      ORDER by combo_id ASC");

$runid = isset($_GET['runid'])? intval($_GET['runid']): 211682;
$year = isset($_GET['year'])? intval($_GET['year']): 2009;
$twp = isset($_GET["twp"])? $_GET["twp"]: 'T78NR19W';



/* Begin Web output! */
$THISPAGE = "township"; include("$_BASE/include/header.phtml");
?>
<h3>Single WEPP run water balance per year</h3>

<p>This application presents the WEPP modelled daily water balance for a 
given IDEP modelling point over a given year.

<form method="GET" action="wb_fe.php">
<strong>Run ID Number:</strong> <input type="text" value="<?php echo $runid; ?>" name="runid" size="10">
&nbsp; <strong>Year:</strong> <?php echo yearSelect(1997,$year,"year"); ?>
<input type="submit" value="Generate Graph">
</form>

<p>
<img src="wb.php?runid=<?php echo $runid; ?>&year=<?php echo $year; ?>">

<p>
<h4>All IDEP runs for this township</h4>

<table cellpadding="3" cellspacing="0" border="1">
<tr><th>Run ID</th><th>HRAP ID</th><th>Management</th><th>Slope</th><th>Length</th></tr>
<tr><th>#</th><th>#</th><th></th><th>%</th><th>feet</th></tr>

<?php
$rs = pg_execute($pgconn, "COMBOS", Array($twp));
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $thisapp = sprintf("wb_fe.php?twp=%s&runid=%s&year=%s", $twp, $row["combo_id"], $year);
  $precipapp = sprintf("../GIS/hrap.phtml?hrap_i=%s", $row["hrap_i"]);
  echo "<tr ";
  if ($row["combo_id"] == $runid) echo "style=\"background:#eee;\"";
  echo "><td><a href=\"$thisapp\">". $row["combo_id"] ."</a></td>
        <td><a href=\"$precipapp\">". $row["hrap_i"] ."</a></td>
    <td><a href=\"$_WEBBASE/meta/management.phtml?man_id=". $row["man_name"] ."\">". $row["man_name"] ."</a></td>
       <td>". $row["steep"] ."</td><td>". $row["len"] ."</td></tr>";
}

?>

</table>

<?php include("$_BASE/include/footer.phtml"); ?>
