#ifndef _CLASSIFIER_H_
#define _CLASSIFIER_H_

#include <string> 
#include <vector>  
#include <iterator>
#include <algorithm>
#include <set>
#include <fstream>

#include "definitions.h"

using namespace std;

struct PredictResult
{
    int label_id;
    string lable;
    double confidence;
};

struct StoryFeature
{
    vector<int> wordIds_np1;   // NP1 list
    vector<int> wordIds_vp;    // VP list
    vector<int> wordIds_np2;   // NP2 list
};

class NBClassifierParameter
{
public:
    int num_categories;
    vector<string> vocabulary_np1;
    vector<string> vocabulary_vp;
    vector<string> vocabulary_np2;
    vector<double> priors_cat;
    Matrix prob_wordsGivenCatsNP1;
    Matrix prob_wordsGivenCatsVP;
    Matrix prob_wordsGivenCatsNP2;

public:
    void Serialize(ostream& os);
    void Unserialize(istream& is);
};

class NaiveBayesClassifier
{
public:
    NaiveBayesClassifier()
    {}

    NaiveBayesClassifier(const string& filename)
    {
        LoadParametersFromFile(filename);
    }

    NaiveBayesClassifier(const NBClassifierParameter& param)
        : param_(param)
    {
        sort(param_.vocabulary_np1.begin(), param_.vocabulary_np1.end());
        sort(param_.vocabulary_vp.begin(), param_.vocabulary_vp.end());
        sort(param_.vocabulary_np2.begin(), param_.vocabulary_np2.end());
    }

    NBClassifierParameter Train(const vector<StoryInfo>& labeled_stories, int num_categories);
    PredictResult Predict(const StoryInfo& story);
    void SaveParametersToFile(const string& filename);
    void LoadParametersFromFile(const string& filename);
protected:
    void ExtractVocabulary(const vector<StoryInfo> & stories)
    {
        set<string> vocabularyNP1, vocabularyVP, vocabularyNP2;
        for(int i=0; i < stories.size(); i++)
        {
            for (int j=0; j < stories[i].words_np1.size(); j++)
            {
                vocabularyNP1.insert(stories[i].words_np1[j]);
            }
            for (int j=0; j < stories[i].words_vp.size(); j++)
            {
                vocabularyVP.insert(stories[i].words_vp[j]);
            }
            for (int j=0; j < stories[i].words_np2.size(); j++)
            {
                vocabularyNP2.insert(stories[i].words_np2[j]);
            }
        }

        param_.vocabulary_np1 = vector<string>(vocabularyNP1.begin(), vocabularyNP1.end());
        sort(param_.vocabulary_np1.begin(), param_.vocabulary_np1.end());

        param_.vocabulary_vp = vector<string>(vocabularyVP.begin(), vocabularyVP.end());
        sort(param_.vocabulary_vp.begin(), param_.vocabulary_vp.end());

        param_.vocabulary_np2 = vector<string>(vocabularyNP2.begin(), vocabularyNP2.end());
        sort(param_.vocabulary_np2.begin(), param_.vocabulary_np2.end());
    }

    // Helper functions for training
    vector<double> CalculatePriors(
        const vector<StoryInfo>& labeled_stories);

    set<string> BuildVocabulary();

    // Helper functions for testing
    StoryFeature ConvertStoryToFeature(const StoryInfo& story);
    vector<int> ConvertWordsToIds(
        const vector<string>& words,
        const vector<string>& vocabulary);

    vector<double> CalcualtePostProbCats(
        const vector<int>& wordIds,
        const Matrix& prob_wordsGivenCats);

    int FindWordId(const vector<string>& vocabulary, const string& word);

protected:
    NBClassifierParameter param_;
};

template <class T>
ostream& operator << (ostream& os, const vector<T>& v)
{
    os << v.size() << endl;
    for (int i = 0; i < v.size(); i++)
    {
        os << v[i] << endl;
    }
    return os;
}

template <class T>
istream& operator >> (istream& is, vector<T>& v)
{
    int size = 0;
    is >> size;
    v.resize(size);

    for (int i = 0; i < v.size(); i++)
    {
        is >> v[i];
    }
    return is;
}

#endif