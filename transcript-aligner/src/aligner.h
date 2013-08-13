#ifndef _ALIGNER_H_
#define _ALIGNER_H_

#include <iostream>
#include <fstream>
#include <memory.h>
#include <sstream>
#include <string>
#include <vector>
#include <assert.h>

#include "string_utility.h"
#include "datetime_utility.h"
#include "person_detector.h"
#include "caption_transcript.h"

// Definitions
#define BEGIN_VIDEO_CLIP    "(BEGIN VIDEO CLIP)"
#define END_VIDEO_CLIP      "(END VIDEO CLIP)"
#define BEGIN_VIDEOTAPE     "(BEGIN VIDEOTAPE)"
#define END_VIDEOTAPE       "(END VIDEOTAPE)"
#define BEGIN_VIDEO_TAPE     "(BEGIN VIDEO TAPE)"
#define END_VIDEO_TAPE       "(END VIDEO TAPE)"
#define BEGIN_AUDIO_CLIP    "(BEGIN AUDIO CLIP)"
#define END_AUDIO_CLIP      "(END AUDIO CLIP)"
#define COMMERCIAL_BREAK    "(COMMERCIAL BREAK)"
#define CHEVRON             ">>"
#define CHEVRON_STORY       ">>>"

// a self-defined flag for easy processing
#define COMMERCIAL_END      "(COMMERCIAL END)"


// For test
#define INPUT_CAPTION       "../data/2012-10-09_1300_US_CNN_Newsroom.txt"
#define INPUT_TRANSCRIPT    "../data/cnr.01.raw"

using namespace std;


//////////////////////////////////////
// Aligner based on Approximate String Matching (Dynamic Programming)

struct Cell
{
    int cost;
    int parent;
};

#define MATCH   0
#define INSERT  1
#define DELETE  2


class AlignmentCounter
{
public:
    AlignmentCounter()
    {
        num_match = 0;
        num_same = 0;
        num_delete = 0;
        num_insert = 0;
        num_keeped = 0;
    }

    int num_match;
    int num_same;
    int num_delete;
    int num_insert;
    int num_keeped;

    void PrintSummary(ostream& os)
    {
        os << "Summary: " << endl;
        os << "    # of words matched:  " << num_match << endl;
        os << "    # of words same:     " << num_same << endl;
        os << "    # of words inserted: " << num_insert << endl;
        os << "    # of words deleted:  " << num_delete << endl;
        os << "    # of words kept:     " << num_keeped << endl;
    }
};

class AlignmentResult
{
public:
    AlignmentResult()
    {
        percentageOfSame = 0;
    }

    Caption alignedCaption;
    double percentageOfSame;
};

class Aligner
{
public:
    Aligner(const Caption* caption, const Transcript* transcript)
    {
        pCaption_ = caption;
        pTranscript_ = transcript;
        table_ = 0;
    }

    ~Aligner()
    {
        DeleteTable();
    }

    const AlignmentResult DoAlign();
private:
    int Compare();
    const Caption ReconstructAndAlign();
    void Reconstruct(int i, int j);
    const Caption BuildTimeAlignedCaption();
    bool isSegmentMark(const string& word);
    void AddEndTimeToTag(vector<CaptionLine>& lines, int index, string timestamp_end);

    void DeleteTable()
    {
        if (table_ != 0)
        {
            for (unsigned int i = 0; i < captionWords_.size(); ++i)
            {
                delete [] table_[i];
                table_[i] = 0;
            }
            delete [] table_;
            table_ = 0;
        }
    }

    void InitTable()
    {
        if (table_ != 0)
        {
            DeleteTable();
        }

        // create a table
        table_ = new Cell*[captionWords_.size()];
        for (unsigned int i = 0; i < captionWords_.size(); ++i)
        {
            table_[i] = new Cell[transcriptWords_.size()];
        }

        for (unsigned int i = 0; i < transcriptWords_.size(); ++i)
        {
            table_[0][i].cost = i;
            if (i > 0)
            {
                table_[0][i].parent = INSERT;
            }
            else
            {
                table_[0][i].parent = -1;
            }
        }

        for (unsigned int i = 0; i < captionWords_.size(); ++i)
        {
            table_[i][0].cost = i;
            if (i > 0)
            {
                table_[i][0].parent = DELETE;
            }
            else
            {
                table_[i][0].parent = -1;
            }
        }
    }

    int MatchCost(const string& cap, const string& trans);
    int InsertCost(const string& trans);
    int DeleteCost(const string& cap, const string& trans);

    int GoalCellCost()
    {
        int i = captionWords_.size() - 1;
        int j = transcriptWords_.size() - 1;
        return (table_[i][j].cost);
    }

    void PerformMatch(unsigned int i, unsigned int j);
    void PerformInsert(unsigned int i, unsigned int j);
    void PerformDelete(unsigned int i, unsigned int j);

private:
    const Caption* pCaption_;
    const Transcript* pTranscript_;
    AlignmentCounter counter_;

    vector<string> captionWords_;
    vector<string> transcriptWords_;
    Cell** table_;

    vector<string> resultWords_;
    vector<int> resultLineLengths_;

    PersonDetector personDetector_;

    // helper variables for recover timestamp
    unsigned int iCurrentLine_;
    unsigned int currentLineBoundary_;
};

#endif
