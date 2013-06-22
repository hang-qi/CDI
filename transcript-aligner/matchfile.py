import sys
import string
import codecs
import re
import datetime
import calendar

# my script
import htmlparser
import timezone
import config

# This is the program name mapping for matching the target caption file
#   Key: the program name appears in the head section of CNN transcript
#   Value: the program name appears in caption filename, eg. .._US_CNN_Program_Name.txt
# For program names that are not in this Dict, they will be converted by
# convert_program_name().
programDict = {
    "AMERICAN MORNING":             "American_Morning",
    "ANDERSON COOPER 360 DEGREES":  "Anderson_Cooper_360",
    "CNN LARRY KING LIVE":          "Larry_King_Live",
    "CNN LATE EDITION WITH WOLF BLITZER": "Late_Edition_With_Wolf_Blitzer",
    "CNN NEWSROOM":                 "Newsroom",
    "DL HUGHLEY BREAKS NEWS":       "DL_Hughley_Breaks_The_News",
    "ERIN BURNETT OUT FRONT":       "Erin_Burnett_Out_Front",
    "IN THE ARENA":                 "In_The_Arena",
    "JOHN KING USA":                "John_King_USA",
    "LOU DOBBS TONIGHT":            "Lou_Dobbs_Tonight",
    "PAULA ZAHN NOW":               "Paula_Zahn_Now",
    "PIERS MORGAN TONIGHT":         "Piers_Morgan_Tonight",
    "THE SITUATION ROOM":           "Situation_Room",
    "YOUR WORLD TODAY":             "Your_World_Today"
}

# Words will keep capitalized in file name, usually a acronym.
#   e.g. we want to keep "CNN" instead of "Cnn", "USA" instead of "Usa".
acronymList = ['CNN', 'USA']


def convert_program_name(programName):
    if programName in programDict:
        return programDict[programName]

    words = programName.replace('/', ' ').split(' ')
    newName = ''
    for w in words:
        if (w == 'THE'):
            continue        # skip 'the'

        if not w in acronymList:
            w = w.lower()
            w = w.replace(w[0], w[
                          0].upper(), 1)  # make the first letter capitalized

            # Get rid of punctuation
            punctuation = False
            t = []
            for i in range(0, len(w)):
                if not w[i].isalnum():
                    punctuation = True
                elif punctuation == True and w[i].isalpha():
                    t.append(w[i].upper())
                    punctuation = False
                else:
                    t.append(w[i])
            w = ''.join(t)

        newName += (w + '_')
    newName = newName.rstrip('_')
    # strip the last '_' at the end
    return newName


def extract_program_info(html_transcript):
    # read in html_transcript
    str_list = []
    f = codecs.open(html_transcript, encoding='ISO-8859-1')
    for line in f:
        str_list.append(line)
    f.close()
    transcriptPage = ''.join(str_list)

    # feed html_transcript into the html parser
    parser = htmlparser.TranscriptHTMLParser()
    parser.feed(transcriptPage)

    # extract program name from head section
    head = parser.get_head()
    et_dt = parser.get_time()

    program_name = head.replace("(HEAD) ", "").replace('\n', '')
    utc_datetime = et_dt.astimezone(timezone.UTC())

    return (program_name, utc_datetime)


def get_transcript_caption_pair(html_transcript):
    """Return matched caption filenames with full path
    The return is a list with two element (transcript file, caption file)"""

    (program, utc_dt) = extract_program_info(html_transcript)
    network = 'CNN'

    # Several special cases using 'HLN' as network flag.
    if program.upper() in ['CNN IN SESSION', 'DR CONRAD MURRAY SENTENCING', 'GEORGE ZIMMERMAN TRIAL LIVE', 'HEADLINE NEWS', 'NANCY GRACE']:
        network = 'HLN'
    if program.upper() == 'NANCY GRACE' and utc_dt < datetime.datetime(2010, 12, 19, tzinfo=timezone.UTC()):
        network = 'CNN-Headline'

    transcript_caption_pair = buildFilenames(utc_dt, program, network)
    return transcript_caption_pair


def round_to_half_hour(dt):
    """Round to the nearest hour or half hour."""
    margin = 5
    if (dt.minute in range(0, margin)):
        dt = dt.replace(minute=0)
    elif (dt.minute in range(60 - margin, 60)):
        dt = dt.replace(minute=0)
        dt = dt + datetime.timedelta(hours=1)
    elif (dt.min in range(30 - margin, 30 + margin)):
        dt = dt.replace(minute=30)
    return dt


def buildFilenames(utcDatetime, program, network='CNN', locale='US'):
    """Return matched filenames with full path.
    The return si a list with two element (transcript file, caption file)."""
    transcriptRoot = config.ROOT_TRANSCRIPT
    captionRoot = config.ROOT_CAPTION

    # Round utc time to hour or half hour.
    utcRoundedDatetime = round_to_half_hour(utcDatetime)
    date_path = "{:%Y/%Y-%m/%Y-%m-%d/}".format(utcRoundedDatetime)

    if not utcRoundedDatetime == utcDatetime:
        print("[TIME ALERT] Time in transcript rounded for {0} on {1:%Y-%m-%d} from {2:%H:%M} to {3:%H:%M}".format(
              program, utcDatetime, utcDatetime, utcRoundedDatetime))

    # Convert program name to the format of file name.
    programName = convert_program_name(program)
    print('[RENAME] Program {0} renamed as {1}.'.format(
        program, programName))

    aired_datetime = "{:%Y-%m-%d_%H%M}".format(utcRoundedDatetime)
    filename = "{aired_datetime}_{locale}_{network}_{program}".format(
        aired_datetime=aired_datetime, locale=locale, network=network, program=programName)

    fullPathFormat = "{root}{date_path}{filename}.{ext}"
    transcriptFullPath = fullPathFormat.format(
        root=transcriptRoot, date_path=date_path, filename=filename, ext="html")
    captionFullPath = fullPathFormat.format(
        root=captionRoot, date_path=date_path, filename=filename, ext="txt")
    return (transcriptFullPath, captionFullPath)


def main():
    if (len(sys.argv) < 2):
        print("Please give a html transcript filename.")
        print("  e.g. > Python3 matchfile.py data/transcript.html")
        filelist

    return sys.argv[1:]
    for filename in filelist:
        print(get_transcript_caption_pair(filename))

if __name__ == '__main__':
    main()
