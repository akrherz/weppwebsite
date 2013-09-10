#set echo
if ($# != 5) then
        echo "Usage:: csh getStage4.csh YYYY MO DD HR DELAY"
        exit 0
endif


set ncep="ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/hourly/prod/"
set YYYY=${1}
set MO=${2}
set DD=${3}
set HR=${4}
set DELAY=${5}

set nh="`python nexthour.py ${YYYY} ${MO} ${DD} ${HR}`"
set YYYY="`echo $nh | cut -c 1-4`"
set MO="`echo $nh | cut -c 5-6`"
set DD="`echo $nh | cut -c 7-8`"
set HR="`echo $nh | cut -c 9-10`"

set dir="${YYYY}/${YYYY}${MO}${DD}"
set stagef="ST4.${YYYY}${MO}${DD}${HR}.01h.Z"
set staget="ST2ml${YYYY}${MO}${DD}${HR}.Grb.Z"

# First, lets always try to get stage2 data
mkdir -p /mnt/idep/data/rainfall/stage2/$dir
wget -q -O $staget ${ncep}/nam_pcpn_anal.${YYYY}${MO}${DD}/ST2ml${YYYY}${MO}${DD}${HR}.Grb.gz
set l="`wc -l $staget | cut -f 1 -d ' '`"
if (${l} == 0 && ${DELAY} < 18) then
	echo "DANGER DANGER. stage2 missing! $staget"
else
	cp $staget /mnt/idep/data/rainfall/stage2/$dir/
endif
rm $staget

# Only get stage4 after 12 hours?
if (${DELAY} < 18) then
	exit 0
endif


mkdir -p /mnt/idep/data/rainfall/stage4/$dir
wget -q -O $stagef ${ncep}/nam_pcpn_anal.${YYYY}${MO}${DD}/ST4.${YYYY}${MO}${DD}${HR}.01h.gz
set l="`wc -l $stagef | cut -f 1 -d ' '`"
if (${l} > 0) then
  cp $stagef /mnt/idep/data/rainfall/stage4/$dir/$stagef 
endif
rm $stagef

exit 0
