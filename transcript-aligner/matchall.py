import os
import sys
import matchfile
import datetime
import subprocess

import config


# Tranverse all files under given dir, save all filenames in a list.
def getHTMLFiles(directory):
    files = []
    for dirpath, dirnames, filenames in os.walk(directory):  # Walk directory tree
        for filename in filenames:
            if (filename[-5:].lower() == ".html"):
                files.append(os.path.join(dirpath, filename))
    return files


def renameHTMLTranscript(oldFilename, newFilename):
    """rename the html transcript by cp."""
    if not os.path.exists(newFilename):
        # os.system("cp -p {src} {tgt}".format(src=oldFilename,
        # tgt=newFilename))
        r = subprocess.call(['cp', '-p', oldFilename, newFilename])
        print('[GOOD] HTML renamed: {0}'.format(newFilename))
    else:
        print('[GOOD] HTML exists: {0}'.format(newFilename))
    return True


def matchAll(htmlTranscriptFiles):
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
            matchedFilenames = matchfile.getMatchedFilenames(
                originalHTMLTranscript)
            targetHTMLFilename = matchedFilenames[0]
            targetCaptionFilename = matchedFilenames[1]

            if (len(targetHTMLFilename) == 0):
                continue

            captionExist = False
            transcriptExist = False

            # check if the caption file with same name exists
            if not os.path.exists(targetCaptionFilename):
                print('[MISSING ALERT] Caption missing at {0}'.format(
                    targetCaptionFilename))
            else:
                print('[GOOD] Caption found at {0}'.format(
                    targetCaptionFilename))
                captionExist = True

            # rename HTML transcript file
            transcriptExist = renameHTMLTranscript(
                originalHTMLTranscript, targetHTMLFilename)

            # run html parser to generate rawtxt for renamed html transcript
            # file.
            if (transcriptExist):
                # os.system("python3 htmlparser.py
                # {transcript}".format(transcript=targetHTMLFilename))
                r = subprocess.call(
                    ['python3', config.ROOT_SCRIPT + 'htmlparser.py', targetHTMLFilename])

            # run aligner, given caption file and raw txt file
            if (captionExist and transcriptExist):
                parsedTranscriptFilename = targetHTMLFilename.replace(
                    ".html", ".rawtxt")
                r = subprocess.call(
                    [config.ROOT_ALIGNER + 'aligner', targetCaptionFilename, parsedTranscriptFilename])
                num_integrated += 1
                num_dayintegrated += 1
            pass
        except:
            print("[ERROR] ", sys.exc_info()[0])
        finally:
            pass
    return num_integrated


def main():
    if (len(sys.argv) < 2):
        print("Please give a folder of transcripts.")
        print("  e.g. > Python3 matchfile.py data/")
        return

    dt_start = datetime.datetime.now()
    transcriptFolder = sys.argv[1]
    print("Processing Transcript directory:" + transcriptFolder)
    print("Traversing...")
    htmlTranscriptFiles = getHTMLFiles(transcriptFolder)
    print("Making copies...")
    num_integrated = matchAll(htmlTranscriptFiles)
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
