#!/bin/csh
  
set yr=$1
set mo=$2
set dy=$3
  
cd /mesonet/data/nexrad/NIDS/DMX
foreach site (ARX DMX DVN FSD MPX OAX)
 echo ${site}
 cd ../${site}
 rm -f NCR/NCR_${1}${2}${3}_*
end

