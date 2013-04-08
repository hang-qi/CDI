#!/bin/bash

# Deploy ner module (tSegment.jar) to /usr/local/bin folder

src_dir='/home/csa/CAS2/Mingjie/tSegment/'
target_dir='/usr/local/bin/tSegment/'

echo Deploying ner...
cp generate-ner.sh /usr/local/bin

cd ${src_dir}
cp tSegment.jar ${target_dir}
cp -r lib ${target_dir}
cp -r Data ${target_dir}
echo Done.