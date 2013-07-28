#!/bin/bash

# This will deploy transcript-aligenr to /usr/local/bin folder

# Deploy shall be conducted with 'qihang' account to have the write permission to bin folder.

echo Deploying transcript-aligner...
cp scripts/*.py /usr/local/bin/transcript_aligner/
cp bin/aligner /usr/local/bin/transcript_aligner/bin/
echo Done.
