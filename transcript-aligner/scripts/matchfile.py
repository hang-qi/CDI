import sys
import codecs
import datetime

# my script
import htmlparser
import timezone
import config

# This is the program name mapping for matching the target caption file
#   Key: the program name appears in the head section of CNN transcript
#   Value: the program name appears in caption filename, eg. .._US_CNN_Program_Name.txt
# For program names that are not in this Dict, they will be converted by
# _convert_program_name().
program_dict = {
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
acronym_list = ['CNN', 'USA']


def get_transcript_caption_pair(html_transcript):
    """Return matched caption filenames with full path
    The return is a list with two element (transcript file, caption file)"""

    (program, utc_dt) = _extract_program_info(html_transcript)
    network = 'CNN'

    # Several special cases using 'HLN' as network flag.
    if program.upper() in ['CNN IN SESSION', 'DR CONRAD MURRAY SENTENCING', 'GEORGE ZIMMERMAN TRIAL LIVE', 'HEADLINE NEWS', 'NANCY GRACE']:
        network = 'HLN'
    if (program.upper() == 'NANCY GRACE' and
        utc_dt < datetime.datetime(2010, 12, 19, tzinfo=timezone.UTC())):
        network = 'CNN-Headline'

    transcript_caption_pair = _build_filenames(utc_dt, program, network)
    return transcript_caption_pair


def _extract_program_info(html_transcript):
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


def _build_filenames(utc_datetime, program, network='CNN', locale='US'):
    """Return matched filenames with full path.
    The return si a list with two element (transcript file, caption file)."""
    transcript_root = config.ROOT_TRANSCRIPT
    caption_root = config.ROOT_CAPTION

    # Round utc time to hour or half hour.
    utc_rounded_datetime = _round_to_half_hour(utc_datetime)
    date_path = "{:%Y/%Y-%m/%Y-%m-%d/}".format(utc_rounded_datetime)

    if not utc_rounded_datetime == utc_datetime:
        print("[TIME ALERT] Time in transcript rounded for {0} on {1:%Y-%m-%d} from {2:%H:%M} to {3:%H:%M}".format(
              program, utc_datetime, utc_datetime, utc_rounded_datetime))

    # Convert program name to the format of file name.
    program_name = _convert_program_name(program)
    print('[RENAME] Program {0} renamed as {1}.'.format(
        program, program_name))

    aired_datetime = "{:%Y-%m-%d_%H%M}".format(utc_rounded_datetime)
    filename = "{aired_datetime}_{locale}_{network}_{program}".format(
        aired_datetime=aired_datetime, locale=locale,
        network=network, program=program_name)

    full_path_format = "{root}{date_path}{filename}.{ext}"
    transcript_full_path = full_path_format.format(
        root=transcript_root, date_path=date_path,
        filename=filename, ext="html")
    caption_full_path = full_path_format.format(
        root=caption_root, date_path=date_path,
        filename=filename, ext="txt")
    return (transcript_full_path, caption_full_path)


def _convert_program_name(program_name):
    if program_name in program_dict:
        return program_dict[program_name]

    words = program_name.replace('/', ' ').split(' ')
    newName = ''
    for w in words:
        if (w == 'THE'):
            continue        # skip 'the'

        if not w in acronym_list:
            # make the first letter capitalized
            w = w.lower()
            w = w.replace(w[0], w[0].upper(), 1)

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
    # strip the last '_' at the end
    newName = newName.rstrip('_')
    return newName


def _round_to_half_hour(dt):
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
