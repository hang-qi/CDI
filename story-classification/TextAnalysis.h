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

struct FinalTriplet 
{
    string StoryName;
    int num_sentences;
    int tripletsIdx;
    string Non_Ph1;
    string Verb_Ph;
    string Non_Ph2;

};

struct TaggedElements 
{
    string Org;     // organization
    string Per;     // person
    string Misc;
};

struct StorySentInfo
{
    string storyTopic;
    int num_sentences;
};


struct TopicElements 
{
    string StoryTimeStart;
    string StoryTimeEnd;
    string StoryTopicName;
    string FullTopicName;
    string Non_Ph1;
    string Verb_Ph;
    vector<string> Person;
    vector<string> Location;
    vector<string> Resources;
    vector<string> Goal;
};


struct StoryElements 
{
    double StoryTimeStart;
    double StoryTimeEnd;
    string StoryCat;
    string StoryTopic;
    string Words;

};

struct StoryElements1 
{
    string StoryTimeStart;
    string StoryTimeEnd;
    string StoryCat;
    string StoryTopic;
    string Words;
};


struct ScreenText 
{
    double Screen_Frame1;   // Time stamp
    double Screen_line1;    // 
    double Base;
    string Screen_Topic;    // On-screen text

};

// combined ScreenText and StoryElements
struct ScreenInfo 
{
    double StoryTimeStart;  // annotated story SegStart
    double StoryTimeEnd;    // annotated story SegEnd
    string StoryTopicName;  // annotated topic
    string CatName;         // annotated category name
    string Screen_words;    // On-screen text

};

struct WordCount 
{
    string Word;
    int Occurance;
};


class TextAnalysis
{
public:
    TextAnalysis();
    ~TextAnalysis();

    //
    // On Screen Text
    //
    void Screen_Text_Info(
        OUT vector<ScreenInfo>& Screen_Info_Final,
        OUT set<string>& Sceen_Words_Vocab,
        const string& orcDir,
        const string& annotatedTextDir, 
        const string& newsListFilename);
    vector<ScreenInfo> RemoveShortStory_ScreenTopic(
        const vector<ScreenInfo> &Screen_Info_Final,
        OUT vector<int> & RemovedStory);
    
    /*
    void SaveVocabulary(set<string> vocabulary, string dest_filename);
    */
    void ParameterLearning_ScreenTopic(vector<ScreenInfo> &Screen_Info_Final,
        const set<string>& vocabulary);

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
    void CalculateSimilarity(const vector<StoryInfo>& StoryWordInfoFinal);

    
    //-----------------------------------
    // Out of date    
    void TransitionMatrix_ScreenTopic(vector<ScreenInfo> &Screen_Info_Final);


    vector<TopicElements> ReadFullDocument(const string& newsListFilename);
    void ReadTagFromFile(vector<TopicElements>& Story_InfoForTag);
    vector<TopicElements> ReadTagFromFile1();
    vector<TopicElements> ReadTag_ResourceGoal(const vector<TopicElements>& Story_InfoForTag);
    void StoryTopic(const vector<TopicElements>& storyInfoTags,
            const vector<TopicElements>& StoryTopicInfo,
            const vector<TopicElements>& resourceGoalTags);
    
private:
    // utilities
    void PrintCrossValidationReport(ostream& os,
        const vector< pair<double, double> >& crossValidation);
};
