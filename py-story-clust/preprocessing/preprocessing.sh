#! /bin/bash

startdate=20080101
enddata=20090101

curdate=$startdate
until [ $curdate == $enddata ]
do
    echo "Processing files in ${curdate}..."

    Y=$(date --date="$curdate" +%Y)
    m=$(date --date="$curdate" +%m)
    d=$(date --date="$curdate" +%d)

    storydir=/dataset/segmented/$Y/$Y-$m/$Y-$m-$d

    curdate=$(date --date="$curdate 1 day" +%Y%m%d)
    python3 preprocessing.py $storydir/\*.seg
done