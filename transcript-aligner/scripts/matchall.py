import os
import sys
import matchfile
import datetime
import subprocess
import re

import config
import htmlparser
import timezone


def getHTMLFiles(directory):
    """Traverse all files under given dir, save all filenames in a list."""
    files = []
    for dirpath, dirnames, filenames in os.walk(directory):  # Walk directory tree
        for filename in filenames:
            if (filename[-5:].lower() == ".html"):
                files.append(os.path.join(dirpath, filename))
    files.sort()
    return files


def renameHTMLTranscript(oldFilename, newFilename):
    """Rename the HTML transcript by cp."""
    if not os.path.exists(newFilename):
        # os.system("cp -p {src} {tgt}".format(src=oldFilename,
        # tgt=newFilename))

        # Make new directory if necessary.
        directory = '/'.join(newFilename.split('/')[0:-1])
        if not os.path.exists(directory):
            os.mkdirs(directory)

        r = subprocess.call(['cp', '-p', oldFilename, newFilename])
        print('[GOOD] HTML renamed: {0}'.format(newFilename))
    else:
        print('[GOOD] HTML exists: {0}'.format(newFilename))
    return True


def matchAll(htmlTranscriptFiles, skipExistingTpt=False):
    dt_dayStart = datetime.datetime.now()
    num_integrated = 0
    num_dayintegrated = 0
    num_daycount = 0

    for originalHTMLTranscript in htmlTranscriptFiles:

        # Time keeping for each day
        dt_dayNow = datetime.datetime.now()
        if not dt_dayStart.day == dt_dayNow.day:
            print("[TIMER] DAY - {0} of {1} transcripts integrated -- runtime {2} on {3:%Y-%m-%d}.".format(
                num_dayintegrated, num_daycount, str(dt_dayNow - dt_dayStart), dt_dayStart))
            num_daycount = 0
            dt_dayStart = dt_dayNow
        num_daycount += 1

        print('-' * 20)
        print('For ' + originalHTMLTranscript.replace(
            os.path.dirname(originalHTMLTranscript), ''))

        try:
            (targetHTMLFilename, targetCaptionFilename) = matchfile.get_transcript_caption_pair(
                originalHTMLTranscript)

            if (len(targetHTMLFilename) == 0):
                continue

            caption_exists = False
            transcript_exists = False

            # Check if the caption file with same name exists.
            if not os.path.exists(targetCaptionFilename):
                print('[MISSING ALERT] Caption missing at {0}'.format(
                    targetCaptionFilename))
            else:
                print('[GOOD] Caption found at {0}'.format(
                    targetCaptionFilename))
                caption_exists = True

            # Rename HTML transcript file.
            transcript_exists = renameHTMLTranscript(
                originalHTMLTranscript, targetHTMLFilename)

            if (transcript_exists):
                # Generate rawtxt for renamed html transcript file.
                parsedTranscriptFilename = htmlparser.convert_to_rawtxt(targetHTMLFilename)
                #r = subprocess.call(
                #    ['python3', config.ROOT_SCRIPT + 'htmlparser.py', targetHTMLFilename])
                tptFilename = targetHTMLFilename.replace('.html', '.tpt')

                # Skip existing tpt files if this option is activated.
                if os.path.exists(tptFilename) and skipExistingTpt:
                    print('[SKIPPED] TPT file exists.')
                    continue

                if not caption_exists:
                    # When caption does not exist, see if the transcript is half hour.
                    # if so combine two rawtxt files and redo the match.
                    aired_datetime = extract_datetime(parsedTranscriptFilename)
                    if (aired_datetime.minute == 30):
                        second_half_rawtxt = parsedTranscriptFilename
                        first_half_rawtxt = replace_airedtime(parsedTranscriptFilename, aired_datetime, aired_datetime.replace(minute=0))
                        targetCaptionFilename = replace_airedtime(targetCaptionFilename, aired_datetime, aired_datetime.replace(minute=0))

                        if os.path.exists(first_half_rawtxt) and os.path.exists(second_half_rawtxt) and os.path.exists(targetCaptionFilename):
                            parsedTranscriptFilename = htmlparser.combine_rawtxt(first_half_rawtxt, second_half_rawtxt)
                            print('[MERGED] Transcript merged: {0} and {1}'.format(first_half_rawtxt, second_half_rawtxt))
                            transcript_exists = True
                            caption_exists = True

            if transcript_exists and caption_exists:
                r = subprocess.call(
                    [config.ROOT_ALIGNER + 'aligner', targetCaptionFilename, parsedTranscriptFilename])
                num_integrated += 1
                num_dayintegrated += 1
            pass
        except ValueError:
            print("[ERROR] ", sys.exc_info()[0])
        #finally:
        #    pass
    return num_integrated


def replace_airedtime(filename, datetime_old, datetime_new):
    return filename.replace('_{:%H%M}_'.format(datetime_old), '_{:%H%M}_'.format(datetime_new))


def extract_datetime(filename):
    filename = filename.split('/')[-1]
    reprog = re.compile(r"""(20\d\d)-(\d\d)-(\d\d)_(\d\d)(\d\d)_.+""", re.I | re.X)
    utcTime = datetime.datetime(2000, 1, 1, 0, 0, tzinfo=timezone.Utc)

    m = reprog.match(filename)
    if not m:
        print("Caption filename is not well-formated.")
        return []

    g = m.groups()
    if not (len(g) == 5):
        print("Caption filename is not well-formated.")
        return []

    utcTime = utcTime.replace(year=int(g[0]),
                              month=int(g[1]),
                              day=int(g[2]),
                              hour=int(g[3]),
                              minute=int(g[4]))
    return utcTime

def main():
    if (len(sys.argv) < 2):
        print('Usage:  Python3 matchall.py [-s] <transcript_folder>')
        print('Option: -s     skip matching if tpt file exists.')
        print('')
        print('e.g. > Python3 matchall.py data/')
        print('e.g. > Python3 matchall.py -s data/')
        return

    transcriptFolder = ''
    skipExistingTpt = False
    if len(sys.argv) == 2:
        transcriptFolder = sys.argv[1]
    elif len(sys.argv) == 3:
        assert(sys.argv[1] == '-s')
        skipExistingTpt = True
        transcriptFolder = sys.argv[2]

    dt_start = datetime.datetime.now()
    print("Processing Transcript directory:" + transcriptFolder)
    print("Traversing...")
    htmlTranscriptFiles = getHTMLFiles(transcriptFolder)
    print("Making copies...")
    num_integrated = matchAll(htmlTranscriptFiles, skipExistingTpt)
    dt_end = datetime.datetime.now()
    print("Done.")

    print('=' * 20)
    print("Time: ")
    print("    Start Time: {0:%Y-%m-%d %H:%M}".format(dt_start))
    print("    End Time:   {0:%Y-%m-%d %H:%M}".format(dt_end))
    print("    Runtime:    {0}".format(str(dt_end - dt_start)))
    print("")
    print("[TIMER] {0} of {1} transcripts integrated -- runtime {2} started at {3:%Y-%m-%d %H:%M}.".format(
        num_integrated, len(htmlTranscriptFiles), str(dt_end - dt_start), dt_start))
    print('=' * 20)

if __name__ == '__main__':
    main()
