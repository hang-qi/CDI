import sys
import re
import datetime
import subprocess
import timezone

import config

class MatchingAlert:
    def __init__(self, captionFilename, transcriptFilename):
        self.captionFilename = captionFilename;
        self.transcriptFilename = transcriptFilename;


# Rematch the given transcript file with a set of caption files,
# determine the best match by the highest similarity score, given by aligner.
def rematch(matchingAlert):
    candidateList = generateCandidiates(matchingAlert.captionFilename);
    parameters = [config.ROOT_ALIGNER + 'aligner', matchingAlert.transcriptFilename];
    parameters.extend(candidateList);
    r = subprocess.call(parameters);
    return

# Returns a list of candidate caption files based on the purposed caption file.
def generateCandidiates(captionFilename):
    reprog = re.compile(r"""/tv/20\d\d/20\d\d-\d\d/20\d\d-\d\d-\d\d/
        (20\d\d)-(\d\d)-(\d\d)_(\d\d)(\d\d)_(.+)""", re.I | re.X);
    candidateList = [];
    utcTime = datetime.datetime(2000,1,1,0,0, tzinfo=timezone.Utc);
    name = "";

    m = reprog.match(captionFilename);
    if not m:
        print("Caption filename is not well-formated.");
        return [];

    g = m.groups();
    if not (len(g) == 6):
        print("Caption filename is not well-formated.");
        return [];

    name = g[5];
    utcTime = utcTime.replace(year = int(g[0]), 
                            month = int(g[1]),
                            day = int(g[2]),
                            hour = int(g[3]),
                            minute = int(g[4]));    
    
    for deltaHour in range(-1, 5):
        newUtcTime = utcTime + datetime.timedelta(hours=deltaHour)
        newFilename = "/tv/{0:%Y/%Y-%m/%Y-%m-%d/%Y-%m-%d_%H%M}_{1}".format(newUtcTime, name);
        candidateList.append(newFilename)        
    return candidateList

    #/tv/2012/2012-01/2012-01-05/2012-01-05_2100_US_CNN_Situation_Room.txt 
    #/tvspare/transcripts/CNN-automated/2012/2012-01/2012-01-05/2012-01-05_2100_US_CNN_Situation_Room.rawtxt

# Returns missing alerts in a list given the alertFilename.
# Each element is an instance of MatchingAlert class.
def getMatchingAlerts(alertFilename):
    reprog = re.compile(r"""^.*\[MATCHING\sALERT\]\s.*
        Caption:\s(.+)\s
        Transcript:\s(.+).*$""", re.I|re.X);
    alerts = []
    fr = open(alertFilename, "r")
    for alertLine in fr:
        m = reprog.match(alertLine)
        if m:
            g = m.groups()
            if (len(g) == 2):
                alert = MatchingAlert(g[0], g[1]);
                alerts.append(alert);
            else:
                print("Error: wrong format of alert file");
                break;
        else:
            print("Error: wrong format of alert file");
            break;
    fr.close();
    return alerts;

# Entrance.
# Usage:  > python3 rematch.py match_alerts.txt
# In which the match_alerts.txt shall be grep-ed from the running result of
# matchall.py. It only consists matching alerts, one line each. 
def main():
    if (len(sys.argv)<2):
        print("Usage:");
        print("   > python3 rematch.py match_alerts.txt");
        return

    dt_start = datetime.datetime.now();
    alertsFilename = sys.argv[1];
    matchingAlerts = getMatchingAlerts(alertsFilename);
    print("{0} matching alerts found.".format(len(matchingAlerts)));
    print("Start rematching...");
    for alert in matchingAlerts:
        print('-'*20)
        print("Rematching transcript file: " + alert.transcriptFilename);
        rematch(alert);        
    print("Done. {0} rematchings performed.".format(len(matchingAlerts)));

    dt_end = datetime.datetime.now();
    print('=' * 20);
    print("Time: ");
    print("    Start Time: {0:%Y-%m-%d %H:%M}".format(dt_start));
    print("    End Time:   {0:%Y-%m-%d %H:%M}".format(dt_end));
    print("    Runtime:    {0}".format(str(dt_end - dt_start)));
    print("");  
    print("[TIMER] {0} rematchings performed. -- runtime {1} started at {2:%Y-%m-%d %H:%M}.".format(
        len(matchingAlerts), str(dt_end - dt_start), dt_start));
    print('=' * 20);

if __name__ == '__main__':
    main()
