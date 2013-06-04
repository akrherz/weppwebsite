#!/bin/csh
  
set yr=$1
set mo=$2
set dy=$3
  
cd /mesonet/data/nexrad/NIDS/DMX
  
foreach site (ARX DMX DVN FSD MPX OAX)
 cd ../${site}
 tar -xzf /mesonet/ARCHIVE/nexrad/${yr}_${mo}/${site}_${yr}${mo}${dy}.tgz NCR
end
