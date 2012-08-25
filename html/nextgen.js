var map, tms;
var appstate = {
		lat: 42.0,
		lon: -95.0,
		date: null,
		ltype: 'vsm'
};
var events = {
		1 : {year: 2007, month: 5, day: 6},
		2 : {year: 2004, month: 5, day: 24},
		3 : {year: 2004, month: 9, day: 14},
};
function selectEvent(e){
	setDate( events[e].year, events[e].month, events[e].day);
}
function setType(t){
	$('#'+ t +'_opt').click();
}
function get_my_url (bounds) {
        var res = this.map.getResolution();
        var x = Math.round ((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.round ((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
        var z = this.map.getZoom();

        var path = z + "/" + x + "/" + y + "." + this.type ;
        var url = this.url;
        if (url instanceof Array) {
            url = this.selectUrl(path, url);
        }
        this.layername = 'idep::'+ appstate.ltype +'::'+$.datepicker.formatDate("yy-mm-dd", appstate.date);
        return url + this.service +"/"+ this.layername +"/"+ path;

   }
function get_my_url2(bounds) {
    var res = this.map.getResolution();
    var x = Math.round((bounds.left - this.maxExtent.left)
                    / (res * this.tileSize.w));
    var y = Math.round((this.maxExtent.top - bounds.top)
                    / (res * this.tileSize.h));
    var z = this.map.getZoom();

    var path = z + "/" + x + "/" + y + "." + this.type ;
    var url = this.url;
    if (url instanceof Array) {
            url = this.selectUrl(path, url);
    }
    return url + this.service + "/" + this.layername + "/" + path;

}
function updateDetails(){
	$('#details_details').css('display', 'none');
	$('#details_loading').css('display', 'block');
    $.get('nextgen-details.php', {lat: appstate.lat, lon: appstate.lon,
		date: $.datepicker.formatDate("yy-mm-dd", appstate.date)},
		function(data){
			$('#details_details').css('display', 'block');
			$('#details_loading').css('display', 'none');
			$('#details_details').html(data);
	});

}
function remap(){
	tms.redraw();
}
function setDate(year, month, date){
	appstate.date = new Date(year+"/"+ month +"/"+ date);
	$('#datepicker').datepicker("setDate", appstate.date);
	remap();
	updateDetails();
}
function init(){
	markers = new OpenLayers.Layer.Vector( "Query" );

    var layer_style = OpenLayers.Util.extend({}, OpenLayers.Feature.Vector.style['default']);
    layer_style.fillOpacity = 1;
    layer_style.graphicOpacity = 1;

    /*
     * Blue style
     */
    var style_blue = OpenLayers.Util.extend({}, layer_style);
    style_blue.strokeColor = "black";
    style_blue.fillColor = "green";
    style_blue.graphicName = "circle";
    style_blue.pointRadius = 5;
    style_blue.strokeWidth = 3;
    style_blue.rotation = 45;
    style_blue.strokeLinecap = "butt";
	
	var p4326 = new OpenLayers.Projection('EPSG:4326');
	var p900913 = new OpenLayers.Projection('EPSG:900913');
    tms = new OpenLayers.Layer.TMS(
            'IDEP Data Layer',
            tilecache +'/c/tile.py/',
            {layername      : 'idep',
            service         : '1.0.0',
            type            : 'png',
            visibility      : true,
            getURL          : get_my_url,
            isBaseLayer     : false}
    );

    controls = {
    	attr:  new OpenLayers.Control.Attribution(),
    	nav:  new OpenLayers.Control.TouchNavigation({
                  dragPanOptions: {
                      enableKinetic: true
                  }
         }),
        ls : new OpenLayers.Control.LayerSwitcher(),
        zoom: new OpenLayers.Control.Zoom(),
        drag: new OpenLayers.Control.DragFeature(markers, {
            onComplete: function(feature, pixel) {
                    geo = feature.geometry.clone();
                    geo.transform(map.getProjectionObject(), p4326);
                    appstate.lat = geo.y;
                    appstate.lon = geo.x;
                    updateDetails();
            }
    })

    };
    
    var osm = new OpenLayers.Layer.OSM('OpenStreetMap (Internet)', null, {
        transitionEffect: 'resize',
        visibility : false,
        isBaseLayer : true
    });
    
    var counties = new OpenLayers.Layer.TMS('US Counties',
            tilecache +'/c/c.py/', {
                    layername : 'c-900913',
                    service : '1.0.0',
                    type : 'png',
                    visibility : false,
                    opacity : 1,
                    getURL : get_my_url2,
                    isBaseLayer : false
            });
    var states = new OpenLayers.Layer.TMS('US States',
    			tilecache +'/c/c.py/', {
                    layername : 's-900913',
                    service : '1.0.0',
                    type : 'png',
                    visibility : true,
                    opacity : 1,
                    getURL : get_my_url2,
                    isBaseLayer : false
            });
    var blank = new OpenLayers.Layer("Blank", {
        isBaseLayer : true,
        visibility : false
    });
    var extent =  new OpenLayers.Bounds(-11074808, 4701182, -9780882, 5531594);
    map = new OpenLayers.Map({
          div: 'map',
          //restrictedExtent : extent,
          projection: new OpenLayers.Projection("EPSG:900913"),
          theme: null,
          layers: [blank, osm, tms, counties, states, markers],
          center: new OpenLayers.LonLat(-95, 42),
          zoom: 1
      });
      for(var key in controls) {
          map.addControl(controls[key]);
      }
      map.zoomToExtent(extent);

      $("#datepicker").datepicker({
    	  dateFormat: 'M d, yy',
    	   onSelect: function(dateText, inst) {
    		   appstate.date = $("#datepicker").datepicker("getDate");
    		   remap(); 
    		   updateDetails();
    	   }
      });
      var d = new Date();
      d.setDate( d.getDate() - 1 );
      appstate.date = d;
      $("#datepicker").datepicker('setDate', d);
      
      $( "#radio" ).buttonset();
      $( '#radio input[type=radio]').change(function(){
    	  tms.redraw();
    	  appstate.ltype = this.value;
    	  $('#rampimg').attr('src',"images/"+ appstate.ltype +"-ramp.png");
      });
      var point = new OpenLayers.Geometry.Point(appstate.lon, appstate.lat);
      var pointFeature = new OpenLayers.Feature.Vector(point.transform(p4326,p900913),null,style_blue);
      markers.addFeatures([pointFeature]);
      
      controls.drag.activate();
      updateDetails();
      
} /* End of init() */
