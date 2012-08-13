
if ($# == 4) then
	# Historical Run
	set yyyy=$1
	set mm=$2
	set dd=$3
	set hr=$4
endif

if ($# == 0) then
	# RT Run
	set yyyy="`date -u --date '4 hours ago' +'%Y'`"
	set mm="`date -u --date '4 hours ago' +'%m'`"
	set dd="`date -u --date '4 hours ago' +'%d'`"
	set hr="`date -u --date '4 hours ago' +'%H'`"
endif

if ($# == 1) then
	# We specify an hours delay
	set yyyy="`date -u --date '${1} hours ago' +'%Y'`"
	set mm="`date -u --date '${1} hours ago' +'%m'`"
	set dd="`date -u --date '${1} hours ago' +'%d'`"
	set hr="`date -u --date '${1} hours ago' +'%H'`"
endif

# First we clean!
rm -f tmp/* 
rm -f nexrad_hrap/*
rm -f ncep_hrap/*

cd scripts

foreach rad (DMX DVN ARX MPX FSD OAX)
	./convertZNIDS.sh $rad $yyyy $mm $dd $hr
	./create15minRef.py $rad $yyyy $mm $dd $hr
end

#echo "./getStage4.csh $yyyy $mm $dd $hr $1"
./getStage4.csh $yyyy $mm $dd $hr $1
./processStage4.csh $yyyy $mm $dd $hr

./combine.py $yyyy $mm $dd $hr
