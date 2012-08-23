var map, tms;
var ltype = 'vsm';

function get_my_url (bounds) {
        var res = this.map.getResolution();
        var x = Math.round ((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.round ((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
        var z = this.map.getZoom();

        var path = z + "/" + x + "/" + y + "." + this.type +"?"+ parseInt(Math.random()*9999);
        var url = this.url;
        if (url instanceof Array) {
            url = this.selectUrl(path, url);
        }
        this.layername = 'idep::'+ ltype +'::'+$.datepicker.formatDate("yy-mm-dd", $("#datepicker").datepicker("getDate"));
        return url + this.service +"/"+ this.layername +"/"+ path;

   }
function get_my_url2(bounds) {
    var res = this.map.getResolution();
    var x = Math.round((bounds.left - this.maxExtent.left)
                    / (res * this.tileSize.w));
    var y = Math.round((this.maxExtent.top - bounds.top)
                    / (res * this.tileSize.h));
    var z = this.map.getZoom();

    var path = z + "/" + x + "/" + y + "." + this.type + "?"
                    + parseInt(Math.random() * 9999);
    var url = this.url;
    if (url instanceof Array) {
            url = this.selectUrl(path, url);
    }
    return url + this.service + "/" + this.layername + "/" + path;

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
            'http://iem.local/cache/tile.py/',
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
                    $('#details').html('Loading...');
                    
                    $.get('nextgen-details.php', {lat: geo.y, lon: geo.x,
                    		date: $.datepicker.formatDate("yy-mm-dd", $("#datepicker").datepicker("getDate"))},
                    		function(data){
                    			$('#details').html(data);
                    });
                    
            }
    })

    };
    /*
    var osm = new OpenLayers.Layer.OSM('OpenStreetMap', null, {
        transitionEffect: 'resize'
    });
    */
    var counties = new OpenLayers.Layer.TMS('US Counties',
            'http://iem.local/c/c.py/', {
                    layername : 'c-900913',
                    service : '1.0.0',
                    type : 'png',
                    visibility : false,
                    opacity : 1,
                    getURL : get_my_url2,
                    isBaseLayer : false
            });
    var states = new OpenLayers.Layer.TMS('US States',
            'http://iem.local/c/c.py/', {
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
          layers: [blank, tms, counties, states, markers],
          center: new OpenLayers.LonLat(-95, 42),
          zoom: 1
      });
      for(var key in controls) {
          map.addControl(controls[key]);
      }
      map.zoomToExtent(extent);

      $("#datepicker").datepicker({
    	   onSelect: function(dateText, inst) { 
    		   tms.redraw(); 
    	   }
      });
      var d = new Date();
      d.setDate( d.getDate() - 1 );
      $("#datepicker").datepicker('setDate', d);
      
      $( "#radio" ).buttonset();
      $( '#radio input[type=radio]').change(function(){
    	  tms.redraw();
    	  ltype = this.value;
      });
      var point = new OpenLayers.Geometry.Point(-92., 42.);
      var pointFeature = new OpenLayers.Feature.Vector(point.transform(p4326,p900913),null,style_blue);
      markers.addFeatures([pointFeature]);
      
      controls.drag.activate();
      
} /* End of init() */
