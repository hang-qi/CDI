#!/bin/bash
#
# Align transcripts from the networks with closed captioning files
#
# Usage: align-transcripts.sh 5
#        where 5 is the number of days ago (default 3)
#
# Author: Hang Qi - qih@qihang.im
# Date: 2013-01-17
# Source: /home/qihang/Programming/transcript-aligner/align-transcripts.sh
#
# ------------------------------------------------------------------------

# Help screen
if [ "$1" = "-h" -o "$1" = "--help" -o "$1" = "help" ]
 then echo -e "\n\t`basename $0` <number of days ago>"
  echo -e "\n\t\tAlign CNN transcripts with closed captioning files."
  echo -e "\n\tExample:"
  echo -e "\n\t\t`basename $0` 5"
  echo -e "\n\tGenerates tpt files.\n"
   exit
fi

## ---------------------------------
## Configurations
## ---------------------------------

# Root directory for transcripts
TTREE=/tvspare/transcripts/CNN-automated

# Output log directory
root_log=$TTREE/log
if [ ! -d $root_log ] ; then mkdir -p $root_log ; fi

# root of aligner program
root_transcript_aligner=/usr/local/bin/transcript_aligner

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
if [ -n "$1" ] ; then days_ago=$1 ; fi

# Skip existing?
if [ "$2" = "SKIP" ] ; then SKIP=true ; fi

# Identify the target day we want to run on.
start_time=$(date +%Y%m%d%H%M%S)
target_date=$(date -u -d "-${days_ago} day" +%Y%m%d)
echo "Running transcript aigner for archives on ${days_ago} days ago."
echo "Date to generate (UTC): ${target_date}"
echo

# Trees
DDIR="${target_date:0:4}/${target_date:0:4}-${target_date:4:2}/${target_date:0:4}-${target_date:4:2}-${target_date:6:2}"
TDIR=$TTREE/$DDIR

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

if [ "$SKIP" = "true" ]
  then echo "[Step 1] Running matchall scripts to match all files (skip existing) ..."
    ($the_python $the_matchall_py -s $TDIR | tee $matchlogfile)
    echo "........ Done!" ; sleep 1
    echo
  else echo "[Step 1] Running matchall scripts to match all files..."
    ($the_python $the_matchall_py $TDIR | tee $matchlogfile)
    echo "........ Done!" ; sleep 1
    echo
fi

##
## 2. Check output for matching alert
##
echo "[Step 2] Checking any matching alerts..."
(grep MATCHING\ ALERT $matchlogfile | tee $alertsfile)
echo "........ Done!" ; sleep 1
echo

##
## 3. For matching alerts, run rematch.py
##
echo "[Step 3] Run the rematch script to match on a broader range..."
($the_python $the_rematch_py $alertsfile | tee $rematchlogfile)
echo "........ Done!" ; sleep 1
echo

# Number of files created
NUM="$( ls -1 $TDIR/*.tpt | wc -l )"

# Receipt
echo -e "\n\tCreated $NUM .tpt files for ${TDIR#*/}\n"

exit

# Copy files to roma and sweep (do this as user tna)
if [ "$NUM" -gt 0 ] ; then
  cp $TDIR/*.tpt /tv/$DDIR/
  rsync /tv/$DDIR/*.tpt roma:/tv/$DDIR/ -av
  rsync /tv/$DDIR/*.tpt ca:/sweep/$DDIR/ -av
fi

# Receipt
echo -e "\n\tCreated $NUM .tpt files for ${DDIR#*/}\n"

# EOF
