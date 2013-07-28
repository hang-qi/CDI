#!/bin/bash
echo Upload transcript-aligner/ with cartago...
rsync -rav ../transcript-aligner/ qihang@ca:/home/qihang/Programming/transcript-aligner/
rsync -rav ../transcript-aligner/ csa@ca:/home/csa/CAS2/hangqi/transcript-aligner/

echo Upload ner/ to cartago...
rsync -rav ../ner/ qihang@ca:/home/qihang/Programming/ner/
rsync -rav ../ner/ csa@ca:/home/csa/CAS2/hangqi/ner/
