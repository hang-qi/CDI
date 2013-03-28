#pragma once
#include <string> 
#include <vector>
#include <set>

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

#define __list_file9 DIR_ROOT "VocabularyOnScreenText.txt"
#define __list_file10 DIR_ROOT "VocabularyNon_Ph1.txt"
#define __list_file11 DIR_ROOT "VocabularyVerb_Ph.txt"
#define __list_file12 DIR_ROOT "VocabularyNon_Ph2.txt"

#define NUM_CATEGORIES	27

#define EXCEPTION_TRIPLETS_FILE_CANNOT_OPEN	-1

using namespace std;


struct TripletElements 
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

struct FinalTripletElements 
{
	string StoryName;
	int StoryNUmber;
	int StoryTripletsCount;
	string Non_Ph1;
	string Verb_Ph;
	string Non_Ph2;

};

struct TaggedElements 
{
	string Org;
	string Per;
	string Misc;
};

struct StorySentInfo
{
	string NameOFStoryTopic;
	int NumOFSenInOneStory;
};


struct Remaind_Rows
{
	string Non_Ph1;
	string Verb_Ph;
	string Non_Ph2;
};

struct ParameterOfModel
{
	double prob_cat;
	double prob_StoryGivenCat;
	double Mu;
	double Sigma;
};


struct WordCatInfo
{
	string word;
	string Cat;
	int StNumInList;
	int wordPlaceInDic;
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
	double Screen_Frame1;	// Time stamp
	double Screen_line1;	// 
	double Base;
	string Screen_Topic;	// On-screen text

};

// combined ScreenText and StoryElements
struct ScreenInfo 
{
	double StoryTimeStart;	// annotated story SegStart
	double StoryTimeEnd;	// annotated story SegEnd
	string StoryTopicName;	// annotated topic
	string CatName;			// annotated category name
	string Screen_words;	// On-screen text

};

struct WordCount 
{
	string Word;
	int Occurance;
};


struct StoryInfo 
{

	string StoryTopic;
	vector<string> NP1;
	vector<string> VP;
	vector<string> NP2;

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
		string orcDir,
		string annotatedTextDir, 
		string newsListFilename);
	vector<ScreenInfo> RemoveShortStory_ScreenTopic(
		const vector<ScreenInfo> &Screen_Info_Final,
		vector<int> & RemovedStory);
	void SaveVocabulary(set<string> vocabulary, string dest_filename);
	void ParameterLearning_ScreenTopic(vector<ScreenInfo> &Screen_Info_Final,
		const set<string>& vocabulary);

	//
	// Triplets
	//
	vector<TripletElements> ReadTripletsFile(string tripletsFilename);
	void ReadFullDocument(string list_file3, vector<TopicElements>& Story_InfoForTag );
	void ReadTagFromFile(vector<TopicElements>& Story_InfoForTag);
	void ReadTagFromFile1(vector<TopicElements> &Story_Tag_Info);
	void ReadTag_Resource_Goal(vector<TopicElements>& Story_InfoForTag ,
	 						vector<TopicElements>& Resource_Goal_Tag );
	void StoryTopic(vector<TopicElements>& Story_Tag_Info , vector<TopicElements>& StoryTopicInfo,
			vector<TopicElements>& Resource_Goal_Tag);


	//void GetSimilarityScore(string keyword, vector<BoundaryEntry>& output);
	
	void RemoveShortStory(vector<TripletElements> & StoryWordInfo , vector<TripletElements> & AllLongStories ,
		                  vector<int> & RemovedStory);	
	void GetNumberOfStorySentence(vector<TripletElements> & StoryWordInfo , vector<StorySentInfo> & StoryNameAndSenNum);
	void RemoveStopWords(vector<TripletElements> & StoryWordInfo ,
						 vector<FinalTripletElements> & StoryWordInfoFinal ,
						 vector<StorySentInfo> & StoryNameAndSenNum,
string list_file5 , string list_file6 , string list_file7 , string list_file8 );
	void ExtractVocabularyList(vector<FinalTripletElements> & StoryWordInfoFinal);
	void ParameterLearning(vector<FinalTripletElements> & StoryWordInfoFinal , vector<StorySentInfo> & StoryNameAndSenNum , string list_file5, string list_file9 ,string list_file10 ,string list_file11, string list_file12 );

	//
	// Similarity
	//
	void CalculateSimilarity(vector<FinalTripletElements> & StoryWordInfoFinal);

	
	//-----------------------------------
	// Out of data
	void FirstSentAsTopic(string fileName , vector<TopicElements>& StoryTopicInfo);
	void TransitionMatrix_ScreenTopic(vector<ScreenInfo> &Screen_Info_Final);

	// For Russian Articles
	void TopicOnWebArticle(vector<TopicElements>& ArticleTopicInfo , string list_file4 , string list_file2);
	
	// Reference Vocabulary
	void Generate_Reference_Vocabulary();
	
private:
	static const char* stopwordsArray[];
};






