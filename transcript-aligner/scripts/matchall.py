import os
import sys
import datetime
import subprocess
import re
import htmlparser

import config
import timezone
import matchfile


def get_html_files(directory):
    """Traverse all files under given dir, save all filenames in a list."""
    files = []
    for dirpath, dirnames, filenames in os.walk(directory):  # Walk directory tree
        for filename in filenames:
            if (filename[-5:].lower() == ".html"):
                files.append(os.path.join(dirpath, filename))
    files.sort()
    return files


def rename_html_transcript(old_filename, new_filename):
    """Rename the HTML transcript by cp."""
    if not os.path.exists(new_filename):
        # Make new directory if necessary.
        directory = '/'.join(new_filename.split('/')[0:-1])
        if not os.path.exists(directory):
            os.mkdirs(directory)

        subprocess.call(['cp', '-p', old_filename, new_filename])
        print('[GOOD] HTML renamed: {0}'.format(new_filename))
    else:
        print('[GOOD] HTML exists: {0}'.format(new_filename))
    return True


def match_all(html_transcript_files, skip_existing_tpt=False):
    dt_dayStart = datetime.datetime.now()
    num_integrated = 0
    num_dayintegrated = 0
    num_daycount = 0

    for original_html_transcript in html_transcript_files:

        # Time keeping for each day
        dt_dayNow = datetime.datetime.now()
        if not dt_dayStart.day == dt_dayNow.day:
            print("[TIMER] DAY - {0} of {1} transcripts integrated -- runtime {2} on {3:%Y-%m-%d}.".format(
                num_dayintegrated, num_daycount, str(dt_dayNow - dt_dayStart), dt_dayStart))
            num_daycount = 0
            dt_dayStart = dt_dayNow
        num_daycount += 1

        print('-' * 20)
        print('For ' + original_html_transcript.replace(
            os.path.dirname(original_html_transcript), ''))

        try:
            (target_html_filename, target_caption_filename) = matchfile.get_transcript_caption_pair(
                original_html_transcript)

            if (len(target_html_filename) == 0):
                continue

            caption_exists = False
            transcript_exists = False

            # Check if the caption file with same name exists.
            if not os.path.exists(target_caption_filename):
                print('[MISSING ALERT] Caption missing at {0}'.format(
                    target_caption_filename))
            else:
                print('[GOOD] Caption found at {0}'.format(
                    target_caption_filename))
                caption_exists = True

            # Rename HTML transcript file.
            transcript_exists = rename_html_transcript(
                original_html_transcript, target_html_filename)

            if (transcript_exists):
                # Generate rawtxt for renamed html transcript file.
                parsed_transcript_filename = htmlparser.convert_to_rawtxt(target_html_filename)
                #r = subprocess.call(
                #    ['python3', config.ROOT_SCRIPT + 'htmlparser.py', target_html_filename])
                tptFilename = target_html_filename.replace('.html', '.tpt')

                # Skip existing tpt files if this option is activated.
                if os.path.exists(tptFilename) and skip_existing_tpt:
                    print('[SKIPPED] TPT file exists.')
                    continue

                if not caption_exists:
                    # When caption does not exist, see if the transcript is half hour.
                    # if so combine two rawtxt files and redo the match.
                    aired_datetime = extract_datetime(parsed_transcript_filename)
                    if (aired_datetime.minute == 30):
                        second_half_rawtxt = parsed_transcript_filename
                        first_half_rawtxt = replace_airedtime(parsed_transcript_filename, aired_datetime, aired_datetime.replace(minute=0))
                        target_caption_filename = replace_airedtime(target_caption_filename, aired_datetime, aired_datetime.replace(minute=0))

                        if os.path.exists(first_half_rawtxt) and os.path.exists(second_half_rawtxt) and os.path.exists(target_caption_filename):
                            parsed_transcript_filename = htmlparser.combine_rawtxt(first_half_rawtxt, second_half_rawtxt)
                            print('[MERGED] Transcript merged: {0} and {1}'.format(first_half_rawtxt, second_half_rawtxt))
                            transcript_exists = True
                            caption_exists = True

            if transcript_exists and caption_exists:
                subprocess.call(
                    [config.ROOT_ALIGNER + 'aligner', target_caption_filename, parsed_transcript_filename])
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

    transcript_dir = ''
    skip_existing_tpt = False
    if len(sys.argv) == 2:
        transcript_dir = sys.argv[1]
    elif len(sys.argv) == 3:
        assert(sys.argv[1] == '-s')
        skip_existing_tpt = True
        transcript_dir = sys.argv[2]

    dt_start = datetime.datetime.now()
    print("Processing Transcript directory:" + transcript_dir)
    print("Traversing...")
    html_transcript_files = get_html_files(transcript_dir)
    print("Making copies...")
    num_integrated = match_all(html_transcript_files, skip_existing_tpt)
    dt_end = datetime.datetime.now()
    print("Done.")

    print('=' * 20)
    print("Time: ")
    print("    Start Time: {0:%Y-%m-%d %H:%M}".format(dt_start))
    print("    End Time:   {0:%Y-%m-%d %H:%M}".format(dt_end))
    print("    Runtime:    {0}".format(str(dt_end - dt_start)))
    print("")
    print("[TIMER] {0} of {1} transcripts integrated -- runtime {2} started at {3:%Y-%m-%d %H:%M}.".format(
        num_integrated, len(html_transcript_files), str(dt_end - dt_start), dt_start))
    print('=' * 20)

if __name__ == '__main__':
    main()
