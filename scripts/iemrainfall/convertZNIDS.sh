
NIDS="/mesonet/data/nexrad/NIDS/"

if [ -z $5 ]
then
	echo "Usage:: convertZNIDS.sh RAD YYYY MO DD HR"
	exit 0
fi

RAD="$1"
YYYY="$2"
MO="$3"
DD="$4"
HR="$5"

pattern="${NIDS}/${RAD}/NCR/NCR_${YYYY}${MO}${DD}_${HR}"

ncr_files=`ls -1 ${pattern}* 2> /dev/null`

for F in ${ncr_files}
do
	# Unzip
	./bin/ucnids $F tmp/`basename $F`
	# Convert it into an text array
	./bin/read_raster_RLE tmp/`basename $F` > tmp/${RAD}_`basename $F`.dat
	# Get only the data
	tail -463 tmp/${RAD}_`basename $F`.dat > tmp/${RAD}_`basename $F`.ras
	# Clean up after ourself...
	rm -f tmp/`basename $F` tmp/${RAD}_`basename $F`.dat 
done
