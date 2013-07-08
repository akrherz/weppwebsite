
if ($# != 4) then
        echo "Usage:: csh processStage4.csh YYYY MO DD HR"
        exit 0
endif
  
set YYYY=${1}
set MO=${2}
set DD=${3}
set HR=${4}

set nh="`python nexthour.py ${YYYY} ${MO} ${DD} ${HR}`"
set YYYY="`echo $nh | cut -c 1-4`"
set MO="`echo $nh | cut -c 5-6`"
set DD="`echo $nh | cut -c 7-8`"
set HR="`echo $nh | cut -c 9-10`" 

set dir="${YYYY}/${YYYY}${MO}${DD}"
set stage="ST4.${YYYY}${MO}${DD}${HR}.01h.Z"
set unstage="ST4.${YYYY}${MO}${DD}${HR}.01h"
set fp="/mesonet/wepp/data/rainfall/stage4/$dir/$stage"
set unfp="/mesonet/wepp/data/rainfall/stage4/$dir/$unstage"
if (! -f ${fp} ) then
	set stage="ST2ml${YYYY}${MO}${DD}${HR}.Grb.Z"
	set unstage="ST2ml${YYYY}${MO}${DD}${HR}.Grb"
	set fp="/mesonet/wepp/data/rainfall/stage2/$dir/$stage"
	set unfp="/mesonet/wepp/data/rainfall/stage2/$dir/$unstage"
endif

set out="tmp/S4_${YYYY}${MO}${DD}${HR}"

if (! -f ${fp}) then
	echo "Missing both stage2 and stage4, using empty HRAP"
	cp lib/empty.hrap ncep_hrap/S4_${YYYY}${MO}${DD}${HR}
else
	gunzip $fp
	bin/wgrib $unfp | grep P | bin/wgrib $unfp -i -o $out > tmp/wgrib.dat

	gzip -c $unfp > $fp
	rm -f $unfp

	if (${YYYY} < 2002) then
		echo "Using Old ST4 Reader..."
		bin/readST4-old $out
	else
		bin/readST4 $out
	endif
	mv outIowa.dat ncep_hrap/S4_${YYYY}${MO}${DD}${HR}
endif

bin/killbigvalue ncep_hrap/S4_${YYYY}${MO}${DD}${HR}
