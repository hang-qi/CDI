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


# align captions and transcripts to generate tpt files.
bash align-transcripts.sh 3

# run NER module for tpt files
bash ner.sh 3