<?php 
include("../etc/config.inc.php");
if (isset($_REQUEST["last_name"])){
	$last_name = $_REQUEST["last_name"];
	$first_name = $_REQUEST["first_name"];
	$cell = $_REQUEST["cell"];
	$email = $_REQUEST["email"];
	
	$dbconn = pg_connect($weppdb);
	$rs = pg_prepare($dbconn, "INSERT", "INSERT into registration(
			first_name, last_name, cell, email) values 
			($1, $2, $3, $4) returning id");
	$rs = pg_execute($dbconn, "INSERT", Array($first_name, $last_name, $cell,
			$email));
	$row = pg_fetch_array($rs,0);
	echo "<p><strong>Thank you!  You are number ". $row["id"] ." to register.";
	
	pg_close($dbconn);
	die();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<title>Farm Progress Show Registration</title>
	<link href="/css/base.css" media="all" rel="stylesheet">
	<link href="/css/content.css" media="all" rel="stylesheet">
	<link rel="icon" href="/images/icon.gif" type="image/gif">
	 <link type="text/css" href="css/ui-lightness/jquery-ui-1.8.22.custom.css" rel="stylesheet" />
 <script type="text/javascript" src="js/jquery-1.7.2.min.js"></script>
 <script type="text/javascript" src="js/jquery-ui-1.8.22.custom.min.js"></script>
	<script language="JavaScript" type="text/javascript">
function init(){
	//$('#submitbutton').attr("disabled", "disabled");
}
function popup(content, title){
	$('#dialog').html(content);
	$('#dialog').dialog({modal: true,
		title: title,
		open: function(event, ui){
		     setTimeout("$('#dialog').dialog('close')",3000);
		    }
    });
}
function formHandler(){
	first_name = $('#first_name').attr('value');
	if (first_name.trim() == ""){
		popup('Please fill out first name', 'Error');
		return;
	}
	last_name = $('#last_name').attr('value');
	if (last_name.trim() == ""){
		popup('Please fill out last name', 'Error');
		return;
	}
	cell = $('#cell').attr('value');
	if (cell.trim() == ""){
		popup('Please fill out Cell Phone', 'Error');
		return;
	}
	email = $('#email').attr('value');
	if (email.trim() == ""){
		popup('Please fill out email', 'Error');
		return;
	}
	$.get('reg.php', {first_name: first_name, last_name: last_name,
		email: email, cell: cell}, function(res){
		popup(res, 'Registration Success!');
		$('#last_name').attr('value', '');
		$('#first_name').attr('value', '');
		$('#email').attr('value', '');
		$('#cell').attr('value', '');
	});
}
	</script>
<body onload="init()">
<div id="dialog" title="Registration Complete!" style="display: none;">
	<p>Blank</p>
</div>
	<div class="hwrapper" id="header">

		<div id="ribbon">
			<div class="grids-24">
				<div class="grid-16">
					<h1 class="nameplate">
						<a accesskey="1" href="http://www.iastate.edu/">
							<img alt="Iowa State University" src="/img/sprite.png"/>
						</a>
					</h1>
				</div>
				<div class="grid-8">

				</div>
			</div>
			<div class="grids-24">
				<div class="grid-12">
					<h2 class="site-title"><a href="/"> </a></h2>
				</div>
				<div class="grid-12">
					<h2 class="site-tagline"></h2>
				</div>
			</div>
		</div>
	</div>

<div id="container">
<div class="fwrapper grids-24">
	<div class="grid-24" style="text-align: center;">
	<h1 style="font-size: 2em;">Register to win an Apple IPad or Cyclone Football Tickets!</h1>
	</div>
</div>
<div class="fwrapper grids-24">
<div class="grid-8"><img src="images/football.jpg" width="300"></div>
<div class="grid-8">
<form name="reg">
    <dl class="block-layout">
        <dt><label>First Name</label></dt>
        <dd>
            <input id="first_name" type="text" name="first_name" value="">
        </dd>

        <dt><label>Last Name</label></dt>
        <dd><input id="last_name" type="text" name="last_name" value=""></dd>
        
        <dt><label>Cell Phone</label></dt>
        <dd><input id="cell" type="text" name="cell" value=""></dd>
        
        <dt><label>Email</label></dt>
        <dd><input id="email" type="text" name="email" value=""></dd>
        
        <dt>* Cell Phone &amp; Email only used to contact prize winners.
        
        <dd><input id="submitbutton" type="submit" name="submit" 
        	value="1 am over 18 and please submit registration" onclick="formHandler(); return false;"></dd>
    </dl>
</form>

</div>
<div class="grid-8"><img src="images/ipad.png" width="300" /></div>
</div>

</body>
</html>