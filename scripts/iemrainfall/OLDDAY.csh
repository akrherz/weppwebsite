#!/bin/csh
#set echo

# Historical Run
set yyyy=$1
set mm=$2
set dd=$3

csh archiveNEXRAD.csh $yyyy $mm $dd

foreach hr (00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23)
	echo "PROCESSING HOUR: $hr"
	# First we clean!
	rm -f tmp/*
	rm -f nexrad_hrap/*

	foreach rad (DMX DVN ARX MPX FSD OAX)
		#if ($yyyy > 2001) then
		sh convertZNIDS.sh $rad $yyyy $mm $dd $hr
		#endif
		python create15minRef.py $rad $yyyy $mm $dd $hr
	end

	csh processStage4.csh $yyyy $mm $dd $hr

	python combine.py $yyyy $mm $dd $hr
end

csh deleteNEXRAD.csh $yyyy $mm $dd
