<?php
// Library for plot functions!

function mkclrbar($map, $imgObj, $c, $i) {
  $layer = $map->getLayerByName("singlebox");
//  $white = $map->addColor(255, 255, 255); // 

  //$p = ms_newRectObj();
  //$p->setextent(10, 460, 50, 450);
  //$p->draw($map, $layer, $imgObj, 0, "0");
  //$p->free();

  
  $x = 10;
  $width = 40;
  for ($k=0;$k<9;$k++){
    $x = $x + $width;
    $p = ms_newRectObj();
    $p->setextent($x, 460, $x + $width, 450);
    $cl = ms_newClassObj($layer);
    $st = ms_newStyleObj($cl);
    $st->color->setRGB($c[$k]['r'], $c[$k]['g'], $c[$k]['b']);
    $st->outlinecolor->setRGB(250, 250, 250);
    $cl->label->color->setRGB(250, 250, 250);
    $cl->label->set("type", MS_BITMAP);
    $cl->label->set("size", MS_LARGE);
    $cl->label->set("position", MS_LR);
    $cl->label->set("offsetx", 15);
    $cl->label->set("offsety", 5);
    $p->draw($map, $layer, $imgObj, $k, $i[$k]);
    $p->free();
  }
}

function mkLegendTitle($map, $imgObj, $titlet) {
  $layer = $map->getLayerByName("credits");

  // point feature with text for location
  $point = ms_newpointobj();
  $point->setXY(475, 450);

  $point->draw($map, $layer, $imgObj, "credits",
    $titlet);
}


?>
