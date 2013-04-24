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

class TextAnalysis
{
public:
    TextAnalysis();
    ~TextAnalysis();

    //
    // Triplets
    //
    vector<Triplet> ReadTripletsFile(const string& tripletsFilename);
    vector <StoryInfo> TripletsToStories(const vector<Triplet> & triplets, bool ignoreSeg = false);
    vector<StoryInfo> Lemmatize(const vector<StoryInfo>& stories);
    vector<Sentence> StoryToSentences(const StoryInfo& story);

    vector<string> RemoveStopWords(const vector<string>& words);
    vector<StoryInfo> RemoveStopWords(const vector<StoryInfo> & stories);
    vector<StoryInfo> Cleasing(const vector<StoryInfo> & stories);        
    
    void CrossValidation(
        const vector<StoryInfo>& stories, const int nfold = 10);

    //
    // Similarity
    //
    void CalculateSimilarity(const vector<StoryInfo>& stories);

private:
    // utilities
    void PrintCrossValidationReport(ostream& os,
        const vector< pair<double, double> >& crossValidation);

    int GetCategoryId(string category)
    {
        const static char* arr[] = {"War", "Sports", "Disaster",
        "Accident", "Activism", "Weather", "Social", "Government", 
        "Science-technology", "Religion", "Politics", "International",
        "Lifestyle-leisure", "Labor", "Human-interest", "Health",
        "Environment", "Education", "Business", "Money", "Crime", "Justice",
        "Art-culture", "Celebrity", "Entertainment", "Network", "Commercial"};
        const static vector<string> categories(arr, arr + sizeof arr / sizeof arr[0]);

        int category_id = -1;
        for(int i = 0; i < categories.size(); i++)
        {
            if (category == categories[i])
            {
                category_id = i;
                break;
            }
        }
        return category_id;
    }

    string GetCategoryById(int category_id)
    {
        const static char* arr[] = {"War", "Sports", "Disaster",
        "Accident", "Activism", "Weather", "Social", "Government", 
        "Science-technology", "Religion", "Politics", "International",
        "Lifestyle-leisure", "Labor", "Human-interest", "Health",
        "Environment", "Education", "Business", "Money", "Crime", "Justice",
        "Art-culture", "Celebrity", "Entertainment", "Network", "Commercial"};

        if (category_id < 0 || category_id >= sizeof arr / sizeof arr[0])
        {
            return "NULL";
        }
        return arr[category_id];        
    }
};
