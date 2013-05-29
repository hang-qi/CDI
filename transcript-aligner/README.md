Transcript-aligner
===

Transcript-aligner generates good-quality transcripts (`tpt` files) by aligning recorded close caption files of TV news with transcript
webpages. 

Compile
---

We use `cmake` to accommodate multiple platforms. cmake 2.6+ and gcc 4.7+ are recommended.

    $ mkdir bin    # create bin folder to perform out of source build
    $ cd bin
    $ cmake ..     # use cmake to generate makefile
    $ make         # build the binary file


Usage
---

There are two usages of this program:

Usage 1: to align one pair of file.

    $ ./aligner captionFilename.txt transcriptFilename.rawtxt

Usage 2: to align multiple pairs of files and keep the best match.

    $ ./aligner transcriptFilename.rawtxt captionFilename1.txt captionFilename2.txt ...


Matchall
=== 

Python script `matchall.py` can be used to automatically match all HTML transcript
with captions. This script will convert HTML transcript to raw text (`.rawtxt`),
find the corresponding caption file, and then call `aligner` to perform the match.

Usage:

    python3 matchall.py [-s] <transcript_folder>

    Option:
    -s     skip matching if tpt file exists.

Examples:

    $ python3 matchall.py html-transcript-dir/
    $ python3 matchall.py -s html-transcript-dir/