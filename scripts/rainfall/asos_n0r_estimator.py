"""
Need to try something, better than nothing, estimate of rainfall. Stupid stageIV data is garbage
for dates prior to 2002

For an hour we...
 1) Pull out ASOS observations of 1 hour precip
 2) Create a simple gridded analysis
 3) Use 15 minute nexrad to smear out this data
 4) Write it to 1km 15min PNG files?
"""

