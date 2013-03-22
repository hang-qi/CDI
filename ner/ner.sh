#!/bin/bash

# Script for automated ner
#
# Usage: ner.sh 3
#        where 3 is the number of days ago. Default 3 if not specified.
#
# Author: Hang Qi - qih@qihang.im
# Date: 3/22/2013

## ---------------------------------
## Configurations
## ---------------------------------
# Root directory for tpt files
root_tpt='/tvspare/transcripts/CNN-automated/'
root_ner=root_tpt

# Output log directory
root_log='/home/csa/CAS2/log/'

# root of ner program (jar)
root_ner_jar='/usr/local/bin/ner/tSegment.jar'

## ---------------------------------

##
## 0. Preparation.
##
# Default number of days ago is 3.
days_ago=3
if [ -n "$1" ]
then
    days_ago=$1
fi

# Identify the target day we want to run on.
start_time=$(date +%Y%m%d%H%M%S)
target_date=$(date -u -v-${days_ago}d +%Y%m%d)
echo "Running ner for archives on ${days_ago} days ago."
echo "Date to generate (UTC): ${target_date}"
echo

target_year=${target_date:0:4}
target_month=${target_date:4:2}
target_day=${target_date:6:2}

# Transcript folders.
dir_tpt=${root_tpt}/${target_year}/${target_year}${target_month}/${target_year}${target_month}${target_day}/
dir_output_ner=${root_ner_jar}/${target_year}/${target_year}${target_month}/${target_year}${target_month}${target_day}/

# log files
nerlogfile=${root_log}/ner_${start_time}.log

function try_step {
    "$@"
    status=$?
    if [ $status -ne 0 ]; then
        echo "ERROR with $1"
        exit
    fi
    return $status
}


##
## 1. Run NER module on the selected day.
##
echo "[Step 1] Running NER module on tpt files..."
mkdir -p ${dir_output_ner}
try_step "(java -jar $root_ner_jar -ner $dir_tpt $dir_output_ner | tee $nerlogfile)"
echo "........ Done!"
echo 
