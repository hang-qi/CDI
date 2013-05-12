#! /bin/bash

startdate=20080101
enddata=20090101

curdate=$startdate
until [ $curdate == $enddata ]
do
    Y=$(date --date="$curdate" +%Y)
    m=$(date --date="$curdate" +%m)
    d=$(date --date="$curdate" +%d)

    tptdir=/dataset/full/$Y/$Y-$m/$Y-$m-$d
    mkdir -p /dataset/segmented/$Y/$Y-$m/$Y-$m-$d

    curdate=$(date --date="$curdate 1 day" +%Y%m%d)
    python3 segment.py $tptdir/\*.tpt
done