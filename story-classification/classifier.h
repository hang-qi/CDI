#ifndef _CLASSIFIER_H_
#define _CLASSIFIER_H_

#include <string> 
#include <vector>  
#include <iterator>
#include <algorithm>
#include <set>

#include "definitions.h"

using namespace std;

struct NBClassifierParameter
{
    int num_categories;
    vector<string> vocabulary_np1;
    vector<string> vocabulary_vp;
    vector<string> vocabulary_np2;
    vector<double> priors_cat;
    Matrix prob_wordsGivenCatsNP1;
    Matrix prob_wordsGivenCatsVP;
    Matrix prob_wordsGivenCatsNP2;
};

class NaiveBayesClassifier
{
public:
    NaiveBayesClassifier(const NBClassifierParameter& param)
        : param_(param)
    {
        sort(param_.vocabulary_np1.begin(), param_.vocabulary_np1.end());
        sort(param_.vocabulary_vp.begin(), param_.vocabulary_vp.end());
        sort(param_.vocabulary_np2.begin(), param_.vocabulary_np2.end());
    }

    void Train();
    int Predict(const StoryInfo& story);

protected:
    StoryFeature ConvertStoryToFeature(const StoryInfo& story);
    vector<int> ConvertWordsToIds(
        const vector<string>& words,
        const vector<string>& vocabulary);

    vector<double> CalcualtePostProbCats(
        const vector<int>& wordIds,
        const Matrix& prob_wordsGivenCats);

    int FindWordId(const vector<string>& vocabulary, const string& word)
    {        
        auto low = lower_bound(vocabulary.begin(), vocabulary.end(), word);        
        string wordFound = *low;
        return int(low - vocabulary.begin());
        /*
        if (wordFound == word)
        {
            return int(low - vocabulary.begin());
        }
        else
        {
            return -1;
        }*/
    }

protected:
    NBClassifierParameter param_;
};

#endif