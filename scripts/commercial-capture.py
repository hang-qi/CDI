import os
import sys
import re
import datetime
import codecs

TPT_HEADER_TAGS = ["TOP", "COL", "UID", "DUR", "CMT", "LBT", "LPF", "HED", "TTL", "OBT", "RUN"]

reTimeStamp = re.compile(r"(20\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)\.(\d\d\d)", re.I | re.X);

def getTPTFiles(directory):
    files = []
    for dirpath, dirnames, filenames in os.walk(directory): # Walk directory tree
        for filename in filenames:
            if (filename[-4:].lower() == ".tpt"):
                files.append(os.path.join(dirpath, filename))
    return files

def str2time(timestamp):
    m = reTimeStamp.match(timestamp);
    if m:
        g = m.groups();        
        t = datetime.datetime(
            year = int(g[0]),
            month = int(g[1]),
            day = int(g[2]),
            hour = int(g[3]),
            minute = int(g[4]),
            second = int(g[5]),
            microsecond = int(g[6])*1000);
    else:
        t = datetime.datetime(2000,1,1,0,0,0);
    return t;

def extractCommercials(tptFiles, outputFolder):    
    totalDuration = datetime.timedelta(0)
    numTptProcessed = 0;
    totalBreaks = 0;

    for tpt in tptFiles:
        print('-'*20)
        filename = os.path.split(tpt)[1];
        f = codecs.open(tpt, encoding='ISO-8859-1')
        fo = open(outputFolder + filename.replace(".tpt", ".ad"), "w")
        print("Processing " + tpt + "...")
        isCommercial = False
        numCommercials = 0
        startTime = datetime.datetime(2000,1,1,0,0,0);
        endTime = datetime.datetime(2000,1,1,0,0,0);    
        duration = datetime.timedelta(0)
        for line in f:
            if line[:3] in TPT_HEADER_TAGS:
                fo.write(line)
                continue
            elif line[:8] == "SegStart" and line[-11:-1] == "Commercial":
                fo.write(line)            
                startTime = str2time(line[9:9+len("20061003230006.000")])
                numCommercials += 1
                isCommercial = True
                continue
            elif line[:6] == "SegEnd" and line[-11:-1] == "Commercial":
                fo.write(line)
                endTime = str2time(line[7:7+len("20061003230006.000")])
                duration += (endTime - startTime)
                isCommercial = False
                continue

            if isCommercial:
                fo.write(line)
    
        print("{0} commercial breaks found with duration {1}.".format(
            numCommercials, str(duration)))

        totalDuration += duration
        totalBreaks += numCommercials
        numTptProcessed += 1        
        f.close()
        fo.close()

    print('=' * 20)
    print("Summary:")
    print("  Files processed: {0}.\n  Total # of commercial breaks:  {1}.\n  Total duration of commercials: {2}."
        .format(numTptProcessed, totalBreaks, str(totalDuration)))
    return numTptProcessed

def main():
    if (len(sys.argv) < 3):
        print("Please give a folder of tpts.")
        print("  e.g. > Python3 commercial-capture.py data/ output/")
        return

    transcriptFolder = sys.argv[1]
    outputFolder = sys.argv[2]

    if not os.path.exists(outputFolder):
        print("The output folder does not exist.")
        return

    dt_start = datetime.datetime.now();    
    print("Processing transcript directory:" + transcriptFolder)
    print("Traversing...")
    tptFiles = getTPTFiles(transcriptFolder)
    print("Extracting Commercials...")
    num_processed = extractCommercials(tptFiles, outputFolder)

    dt_end = datetime.datetime.now();

    print('=' * 20);
    print("Time: ");
    print("    Start Time: {0:%Y-%m-%d %H:%M}".format(dt_start));
    print("    End Time:   {0:%Y-%m-%d %H:%M}".format(dt_end));
    print("    Runtime:    {0}".format(str(dt_end - dt_start)));
    print("");  
    print("[TIMER] Commercials from {0} of {1} transcripts have been extracted -- runtime {2} started at {3:%Y-%m-%d %H:%M}.".format(
        num_processed, len(tptFiles), str(dt_end - dt_start), dt_start));
    print('=' * 20);

if __name__ == '__main__':
    main()