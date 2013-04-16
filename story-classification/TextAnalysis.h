#pragma once

#include <string> 
#include <vector>
#include <set>

#include "definitions.h"
#include "classifier.h"

#define OUT

// some path
#define DIR_ROOT "/home/csa/CAS2/hangqi/StoryTextInfo/"

// For Russian Articles
//#define list_file2 DIR_ROOT "WWW_Article/";
//#define list_file4 DIR_ROOT "ArticleList.txt";
//#define list_file15 DIR_ROOT "WWW_Article/";

#define FILE_NEWSLIST DIR_ROOT "NewsList.txt" //    "Screen_TextList";
  
#define DIR_OCR DIR_ROOT "OCR/"   
#define DIR_ANNOTATEDTEXT DIR_ROOT "AnnotededText/" //   /sweep/2008/2008-08/2008-08-08/
    
#define FILE_ANNA_JAR DIR_ROOT "anna.jar"
#define FILE_ANNA_BEFORE_SPLIT DIR_ROOT "anna-before-split.txt"
#define FILE_ANNA_AFTER_SPLIT DIR_ROOT "anna-after-split.txt"
#define FILE_LEMMA_ENG_MODEL DIR_ROOT "lemma-eng.model"

#define NUM_CATEGORIES  27

#define EXCEPTION_TRIPLETS_FILE_CANNOT_OPEN -1

using namespace std;

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

class TextAnalysis
{
public:
    TextAnalysis();
    ~TextAnalysis();

    //
    // Triplets
    //
    vector<Triplet> ReadTripletsFile(const string& tripletsFilename);
    vector <StoryInfo> TripletsToStories(const vector<Triplet> & triplets);
    vector<StoryInfo> Lemmatize(const vector<StoryInfo>& stories);

    vector<string> RemoveStopWords(const vector<string>& words);
    vector<StoryInfo> Cleasing(const vector<StoryInfo> & stories);    
    void ExtractVocabularyList(const vector<StoryInfo> & stories,
        OUT set<string>& vocabularyNP1,
        OUT set<string>& vocabularyVP, 
        OUT set<string>& vocabularyNP2);
    
    void CrossValidation(
        const vector<StoryInfo>& stories,
        const set<string>& vocabularyNP1, 
        const set<string>& vocabularyVP, 
        const set<string>&vocabularyNP2,
        const int nfold = 10);

    //
    // Similarity
    //
    void CalculateSimilarity(const vector<StoryInfo>& stories);

    void GetTransitionMatrix(const vector<StoryInfo>& stories);
    
private:
    // utilities
    void PrintCrossValidationReport(ostream& os,
        const vector< pair<double, double> >& crossValidation);
};
