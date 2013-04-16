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
    string timeStart;
    string timeEnd;
};

struct WordCatInfo
{
    string word;
    string Cat;
    int StNumInList;
    int wordPlaceInDic;
};

#endif