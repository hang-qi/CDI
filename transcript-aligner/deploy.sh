#!/bin/bash

# This will deploy transcript-aligenr to /usr/local/bin folder

echo Deploying transcript-aligner...
cp *.py /usr/local/bin/transcript_aligner/
cp bin/aligner /usr/local/bin/transcript_aligner/bin/
echo Done.