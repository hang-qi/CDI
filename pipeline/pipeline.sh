#!/bin/bash

# Script for automated pipeline.
#   1. align transcript to generate tpt files.
#   2. run NER module for tpt files.
#   3. clean NER outputs.
#
# Usage: pipeline.sh
#
# Author: Hang Qi - qih@qihang.im
# Date: 3/22/2013

days_ago=3
if [ -n "$1" ]
then
    days_ago=$1
fi

# align captions and transcripts to generate tpt files.
bash align-transcripts.sh ${days_ago}

# run NER module for tpt files
bash ner.sh ${days_ago}