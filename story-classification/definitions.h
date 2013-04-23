#ifndef _DEFINITIONS_H_
#define _DEFINITIONS_H_

#include <vector> 
#include <string>

using namespace std;

typedef vector< vector<double> > Matrix;

struct StoryInfo 
{
    string name;            // labeled name    
    int category_id;
    int document_id;
    int num_sentences;      // number of sentences
    vector<string> words_np1;     // NP1 list
    vector<string> words_vp;      // VP list
    vector<string> words_np2;     // NP2 list
    vector<int> len_np1;
    vector<int> len_vp;
    vector<int> len_np2;
    string timeStart;
    string timeEnd;
};

struct Sentence
{
    vector<string> words_np1;     // NP1 list
    vector<string> words_vp;      // VP list
    vector<string> words_np2;     // NP2 list
};

struct Triplet
{
    string StoryTimeStart;
    string StoryTimeEnd;
    string StoryTopicName;
    //int NumOfSentenceInStory;
    string Non_Ph1;
    string Verb_Ph;
    string Non_Ph2;
    //int nTimeInSecond;
};

struct WordCatInfo
{
    string word;
    string Cat;
    int StNumInList;
    int wordPlaceInDic;
};

struct PredictResult
{
    int label_id;
    double joint_prob;
};

struct StoryFeature
{
    vector<int> wordIds_np1;   // NP1 list
    vector<int> wordIds_vp;    // VP list
    vector<int> wordIds_np2;   // NP2 list
};


#endif