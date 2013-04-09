#ifndef _DEFINITIONS_H_
#define _DEFINITIONS_H_

#include <vector> 
#include <string>

using namespace std;

typedef vector< vector<double> > Matrix;

struct StoryInfo 
{
    string name;            // labeled name
    string category;        // category
    int categoryId;         // categoryId
    int num_sentences;      // number of sentences
    vector<string> words_np1;     // NP1 list
    vector<string> words_vp;      // VP list
    vector<string> words_np2;     // NP2 list
};

struct StoryFeature
{
    vector<int> wordIds_np1;   // NP1 list
    vector<int> wordIds_vp;    // VP list
    vector<int> wordIds_np2;   // NP2 list
};


struct WordCatInfo
{
    string word;
    string Cat;
    int StNumInList;
    int wordPlaceInDic;
};

#endif