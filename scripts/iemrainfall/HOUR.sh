
if [ $# -eq 4 ]
then
    # Historical Run
    yyyy=$1
    mm=$2
    dd=$3
    hr=$4
fi

if [ $# -eq 0 ]
then
    # RT Run
    yyyy=$(date -u --date '4 hours ago' +'%Y')
    mm=$(date -u --date '4 hours ago' +'%m')
    dd=$(date -u --date '4 hours ago' +'%d')
    hr=$(date -u --date '4 hours ago' +'%H')
fi

if [ $# -eq 1 ]
then
    # We specify an hours delay
    yyyy=$(date -u --date "${1} hours ago" +'%Y')
    mm=$(date -u --date "${1} hours ago" +'%m')
    dd=$(date -u --date "${1} hours ago" +'%d')
    hr=$(date -u --date "${1} hours ago" +'%H')
fi

# First we clean!
rm -f tmp/* 
rm -f nexrad_hrap/*
rm -f ncep_hrap/*

for rad in $(echo "DMX DVN ARX MPX FSD OAX"); do
    sh convertZNIDS.sh $rad $yyyy $mm $dd $hr
    python create15minRef.py $rad $yyyy $mm $dd $hr
done

#csh getStage4.csh $yyyy $mm $dd $hr $1
csh processStage4.csh $yyyy $mm $dd $hr

python combine.py $yyyy $mm $dd $hr
