#!/bin/bash

# Script for automated alignment
#
# Usage: align-transcripts.sh 3
#        where 3 is the number of days ago. Default 3 if not specified.
#
# Author: Hang Qi - qih@qihang.im
# Date: 1/17/2013

## ---------------------------------
## Configurations
## ---------------------------------
# Root directory for transcripts and captions
root_transcript='/tvspare/transcripts/CNN-automated'
root_captions='/tv'

# Output log directory
root_log=$root_transcript/log
if [ ! -d $root_log ] ; then mkdir -p $root_log ; fi

# root of aligner program
root_transcript_aligner='/usr/local/bin/transcript_aligner'

# location of binary and scripts to the program root
the_matchall_py=${root_transcript_aligner}/matchall.py
the_rematch_py=${root_transcript_aligner}/rematch.py

# The specific python shall be used
the_python=python3
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
target_date=$(date -u -d "-${days_ago} day" +%Y%m%d)
echo "Running transcript aigner for archives on ${days_ago} days ago."
echo "Date to generate (UTC): ${target_date}"
echo

target_year=${target_date:0:4}
target_month=${target_date:4:2}
target_day=${target_date:6:2}

# Transcript folders.
dir_transcripts=${root_transcript}/${target_year}/${target_year}-${target_month}/${target_year}-${target_month}-${target_day}/

# logfiles
matchlogfile=${root_log}/transcript-aligner_${start_time}_match.log
alertsfile=${root_log}/transcript-aligner_${start_time}_alerts.log
rematchlogfile=${root_log}/transcript-aligner_${start_time}_rematch.log


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
## 1. Run the matchall.py to match all files in the day specified.
##
echo "[Step 1] Running matchall scripts to match all files..."
try_step "($the_python $the_matchall_py $dir_transcripts | tee $matchlogfile)"
echo "........ Done!"
echo 

##
## 2. Check output for matching alert
##
echo "[Step 2] Checking any matching alerts..."
try_step "(grep MATCHING\ ALERT $matchlogfile | tee $alertsfile)"
echo "........ Done!"
echo 

##
## 3. For matching alerts, run rematch.py
##
echo "[Step 3] Run the rematch script to match on a broader range..."
try_step "($the_python $the_rematch_py $alertsfile | tee $rematchlogfile)"
echo "........ Done!"
echo 
