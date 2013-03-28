#include <string.h>
#include <vector>
#include <set>
#include <cstdio>
#include <iostream>
#include <string>
#include <fstream>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <math.h>
#include "TextAnalysis.h"
#pragma comment(lib, "User32.lib")
using namespace std; 

int main(int argc, const char* argv[])
{
	vector<StorySentInfo> storyNameAndSenNum ;
	vector<TripletElements> StoryWordInfo, AllLongStories;
	vector<TopicElements> StoryTopicInfo, ArticleTopicInfo, 
			Story_InfoForTag ,Story_Tag_Info, Resource_Goal_Tag;
	vector<ParameterOfModel> ModelParameter;
	vector<FinalTripletElements> StoryWordInfoFinal;
	vector<TaggedElements> StoryTagInfo;
	vector<ScreenInfo> Screen_Info_Final;
	vector<int> RemovedStory;
	vector<string> FullDocument;

	StoryWordInfo.clear();
	ModelParameter.clear();
	AllLongStories.clear();
	StoryWordInfoFinal.clear();
	StoryTagInfo.clear();
	StoryTopicInfo.clear();
	ArticleTopicInfo.clear();
	Screen_Info_Final.clear();
	RemovedStory.clear();
	Story_InfoForTag.clear();
	Story_Tag_Info.clear();
	Resource_Goal_Tag.clear();

	//std:string pathRoot = "/home/csa/CAS2/hangqi/StoryTextInfo/";
	string pathTriplets = "/home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/";

	/*if (argc == 3)
	{
		pathRoot = argv[1]; 	//   /home/csa/CAS2/Arash/StoryTextInfo/   
		pathTriplets = argv[2]; //   /home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/
	}

	
	// Russian news articles
	//string list_file2 = argv[3]; //  /home/csa/CAS2/Arash/StoryTextInfo/WWW_Article/	
	/*
	string list_file2 = pathRoot + "WWW_Article/";
	string list_file4 = pathRoot + "ArticleList.txt";
	string list_file15 = pathRoot + "WWW_Article/";

	string FILE_NEWSLIST = pathRoot + "NewsList.txt"; //    "Screen_TextList";
	  
	string ocrDir = pathRoot + "OCR/";   
	string annotatedTextDir = pathRoot + "AnnotededText/"; //   /sweep/2008/2008-08/2008-08-08/
	
	string list_file5 = pathRoot + "anna.jar";
	string list_file6 = pathRoot + "inout.txt";
	string list_file7 = pathRoot + "lemma-eng.model";
	string list_file8 = pathRoot + "inout1.txt/";

	string list_file9 = pathRoot + "VocabularyOnScreenText.txt";
	string list_file10 = pathRoot + "VocabularyNon_Ph1.txt";
	string list_file11 = pathRoot + "VocabularyVerb_Ph.txt";
	string list_file12 = pathRoot + "VocabularyNon_Ph2.txt";
	*/

	TextAnalysis cws;

	//// This part for Russian news article :
	//	cws.TopicOnWebArticle(ArticleTopicInfo , list_file4 , list_file2);

	//
	// OCR classification
	//
	set<string> screen_vocabulary;
	cws.Screen_Text_Info(
		Screen_Info_Final,
		screen_vocabulary,
		DIR_OCR,
		DIR_ANNOTATEDTEXT,
		FILE_NEWSLIST);
	//cws.Generate_Reference_Vocabulary();
	cws.RemoveShortStory_ScreenTopic(Screen_Info_Final, RemovedStory);
	//cws.SaveVocabulary(screen_vocabulary, "output/onscreentext_vocabulary.txt");
	cws.ParameterLearning_ScreenTopic(Screen_Info_Final, screen_vocabulary);
	//cws.ParameterLearning_ScreenTopic(Screen_Info_Final, "output/onscreentext_vocabulary.txt");


	//
	// Loading triplets files
	//
	ifstream documentList;
	documentList.open(FILE_NEWSLIST, ios::in);
 	if (!documentList.is_open())
 	{
 		cout<<"File in list1.txt NOT opened"<<endl;
 	}
	while (!documentList.eof() && documentList.good())
	{
		char buffer[512];
		documentList.getline(buffer, 512);
		string base = buffer;
		base = base.substr(0 , 15);
		string tripletsFilename = (pathTriplets + base +"_US_CNN_Newsroom.html.align.chunk_coref_triplets.dat");
		
		vector<TripletElements> tmp = cws.ReadTripletsFile(tripletsFilename);
		StoryWordInfo.insert(StoryWordInfo.begin(), tmp.begin(), tmp.end());
		// cws.FirstSentAsTopic(tripletsFilename  , StoryTopicInfo);
	}

	//
	// Triplets classification
	//
	cws.ReadFullDocument(FILE_NEWSLIST, Story_InfoForTag);	
	cws.ReadTagFromFile(Story_InfoForTag);
	cws.ReadTagFromFile1(Story_Tag_Info);
	cws.ReadTag_Resource_Goal(Story_InfoForTag , Resource_Goal_Tag );
	cws.StoryTopic(Story_Tag_Info , StoryTopicInfo, Resource_Goal_Tag);


	cws.RemoveShortStory(StoryWordInfo ,  AllLongStories , RemovedStory);
	cws.GetNumberOfStorySentence(AllLongStories , storyNameAndSenNum);
	cws.RemoveStopWords(AllLongStories ,  StoryWordInfoFinal, storyNameAndSenNum, 
				FILE_ANNA_JAR , FILE_ANNA_BEFORE_SPLIT , FILE_LEMMA_ENG_MODEL , FILE_ANNA_AFTER_SPLIT);
	cws.ExtractVocabularyList(StoryWordInfoFinal);
	cws.ParameterLearning(StoryWordInfoFinal , storyNameAndSenNum , FILE_ANNA_JAR, 
			__list_file9, __list_file10,
			__list_file11, __list_file12);


	// This is for similarity clustering :
	cws.CalculateSimilarity(StoryWordInfoFinal);
	//cws.TransitionMatrix_ScreenTopic(Screen_Info_Final);


  return 0;
}


//  cd /home/csa/CAS2/Arash/StoryTextInfo/
//  ./TextAnalysis /home/csa/CAS2/Arash/StoryTextInfo/ /home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/

//  argv[0] = /home/csa/CAS2/Arash/StoryTextInfo
//  java -Xmx1g -jar WNsim.jar n /home/csa/CAS2/Arash/StoryTextInfo/lemmatized_words.txt
