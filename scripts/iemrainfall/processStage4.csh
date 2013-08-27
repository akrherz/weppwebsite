
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
set stage="ST4.${YYYY}${MO}${DD}${HR}.01h.grib"
set fn="/mesonet/ARCHIVE/data/${YYYY}/${MO}/${DD}/stage4/$stage"
if (! -f ${fn} ) then
	set stage="ST2ml.${YYYY}${MO}${DD}${HR}.01h.grib"
	set fn="/mesonet/ARCHIVE/data/${YYYY}/${MO}/${DD}/stage4/$stage"
endif

set out="tmp/S4_${YYYY}${MO}${DD}${HR}"

if (! -f ${fn}) then
	echo "Missing both stage2 and stage4, using empty HRAP"
	cp lib/empty.hrap ncep_hrap/S4_${YYYY}${MO}${DD}${HR}
else
	bin/wgrib $fn | grep P | bin/wgrib $unfp -i -o $out > tmp/wgrib.dat

	if (${YYYY} < 2002) then
		echo "Using Old ST4 Reader..."
		bin/readST4-old $out
	else
		bin/readST4 $out
	endif
	mv outIowa.dat ncep_hrap/S4_${YYYY}${MO}${DD}${HR}
endif

bin/killbigvalue ncep_hrap/S4_${YYYY}${MO}${DD}${HR}
