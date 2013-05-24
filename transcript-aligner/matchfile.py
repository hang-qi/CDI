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
# For program names that are not in this Dict, they will be converted by convertProgramName().
programDict = {
    "ANDERSON COOPER 360 DEGREES"   : "Anderson_Cooper_360",
    "CNN NEWSROOM"                  : "Newsroom",
    "THE SITUATION ROOM"            : "Situation_Room",
    "CNN LARRY KING LIVE"           : "Larry_King_Live",
    "JOHN KING USA"                 : "John_King_USA",
    "YOUR WORLD TODAY"              : "Your_World_Today",
    "AMERICAN MORNING"              : "American_Morning",
    "PIERS MORGAN TONIGHT"          : "Piers_Morgan_Tonight",
    "ERIN BURNETT OUT FRONT"        : "Erin_Burnett_Out_Front",
    "PAULA ZAHN NOW"                : "Paula_Zahn_Now",
    "LOU DOBBS TONIGHT"             : "Lou_Dobbs_Tonight"
    "IN THE ARENA"                  : "In_The_Arena"
}

# Words will keep capitalized in file name, usually a acronym.
#   e.g. we want to keep "CNN" instead of "Cnn", "USA" instead of "Usa".
acronymList = ['CNN', 'USA']

def convertProgramName(programName):
    words = programName.replace('/',' ').split(' ')
    newName = ''
    for w in words:
        if (w == 'THE'):
            continue        # skip 'the'
        
        if not w in acronymList:
            w = w.lower();
            w = w.replace(w[0], w[0].upper(), 1); # make the first letter capitalized

            # Get rid of punctuation
            punctuation = False;
            t = [];
            for i in range(0, len(w)):
                if not w[i].isalnum():
                    punctuation = True;
                elif punctuation == True and w[i].isalpha():
                    t.append(w[i].upper());                    
                    punctuation = False;
                else:
                    t.append(w[i]);
            w = ''.join(t);

        newName += (w + '_')    
    newName = newName.rstrip('_');              # strip the last '_' at the end
    return newName;

# Return matched caption filenames with full path
# The return is a list with two element (transcript file, caption file)
def getMatchedFilenames(transcriptFile, charset='ISO-8859-1'):
    # read in transcriptFile
    str_list = [];
    f = codecs.open(transcriptFile, encoding=charset)
    for line in f:
        str_list.append(line)
    f.close()
    transcriptPage = ''.join(str_list)

    # feed transcriptFile into the html parser
    parser = htmlparser.TranscriptHTMLParser()
    parser.feed(transcriptPage)

    # extract program name from head section
    head = parser.get_head()
    programName = head.replace("(HEAD) ", "").replace('\n','')
    
    utc = timezone.UTC();
    et_dt = parser.get_time();
    utc_dt = et_dt.astimezone(utc)
    
    return buildFilenames(utc_dt, programName);

# Round to the nearest hour or half hour
def roundToHalfHour(dt):
    margin = 5;
    if (dt.minute in range(0, margin)):
        dt = dt.replace(minute=0)
    elif (dt.minute in range(60-margin, 60)):
        dt = dt.replace(minute=0)
        dt = dt + datetime.timedelta(hours=1)
    elif (dt.min in range(30-margin, 30+margin)):
        dt = dt.replace(minute=30)
    return dt

# Return matched filenames with full path
# The return is a list with two element (transcript file, caption file)
def buildFilenames(utcDatetime, program, agent='CNN', locale='US'):
    transcriptRoot = config.ROOT_TRANSCRIPT
    captionRoot = config.ROOT_CAPTION

    utcRoundedDatetime = roundToHalfHour(utcDatetime)
    dateDirectories = "{:%Y/%Y-%m/%Y-%m-%d/}".format(utcRoundedDatetime)

    if not utcRoundedDatetime == utcDatetime:
        print("[TIME ALERT] Time in transcript rounded for {0} on {1:%Y-%m-%d} from {2:%H:%M} to {3:%H:%M}".format(
                 program, utcDatetime, utcDatetime, utcRoundedDatetime));
    
    programName = '';
    try:
        programName = programDict[program];
        pass
    except:
        programName = convertProgramName(program);
        print('[RENAME] Program {0} renamed as {1}.'.format(program, programName));
        #return ('','')

    airedDateTime = "{:%Y-%m-%d_%H%M}".format(utcRoundedDatetime)
    filename = "{0}_{1}_{2}_{3}".format(airedDateTime, locale, agent, programName)

    
    fullPathFormat = "{root}{dateDir}{file}{ext}"
    transcriptFullPath = fullPathFormat.format(root=transcriptRoot, 
                dateDir=dateDirectories, file=filename, ext=".html")
    captionFullPath = fullPathFormat.format(root=captionRoot, 
                dateDir=dateDirectories, file=filename, ext=".txt")
    return (transcriptFullPath, captionFullPath)

def main():
    if (len(sys.argv) < 2):
        print("Please give a html transcript filename.")
        print("  e.g. > Python3 matchfile.py data/transcript.html")
        return

    filelist = sys.argv[1:]
    for filename in filelist:
        print(getMatchedFilenames(filename))

if __name__ == '__main__':
	main()