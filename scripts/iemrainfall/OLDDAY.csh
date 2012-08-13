#!/bin/csh
#set echo

# Historical Run
set yyyy=$1
set mm=$2
set dd=$3

cd scripts
./archiveNEXRAD.csh $yyyy $mm $dd

foreach hr (00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23)
	echo "PROCESSING HOUR: $hr"
	# First we clean!
	rm -f ../tmp/*
	rm -f ../nexrad_hrap/*

	foreach rad (DMX DVN ARX MPX FSD OAX)
		#if ($yyyy > 2001) then
		./convertZNIDS.csh $rad $yyyy $mm $dd $hr
		#endif
		./create15minRef.py $rad $yyyy $mm $dd $hr
	end

	./processStage4.csh $yyyy $mm $dd $hr

	./combine.py $yyyy $mm $dd $hr
end

./deleteNEXRAD.csh $yyyy $mm $dd
