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
	string pathTriplets = "/home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/";
	/*if (argc == 3)
	{
		pathRoot = argv[1]; 	//   /home/csa/CAS2/Arash/StoryTextInfo/   
		pathTriplets = argv[2]; //   /home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/
	}
	*/

	TextAnalysis cws;

	//// This part for Russian news article :
	// vector<TopicElements> ArticleTopicInfo;
	// cws.TopicOnWebArticle(ArticleTopicInfo , list_file4 , list_file2);

	//
	// OCR classification
	//
	vector<ScreenInfo> screenInfo;
	set<string> screen_vocabulary;
	vector<int> RemovedStory;
	cws.Screen_Text_Info(
		screenInfo,
		screen_vocabulary,
		DIR_OCR,
		DIR_ANNOTATEDTEXT,
		FILE_NEWSLIST);
	//cws.Generate_Reference_Vocabulary();
	screenInfo = cws.RemoveShortStory_ScreenTopic(screenInfo, RemovedStory);
	cws.ParameterLearning_ScreenTopic(screenInfo, screen_vocabulary);
	

	//
	// Loading triplets files
	//
	ifstream documentList;
	documentList.open(FILE_NEWSLIST, ios::in);
 	if (!documentList.is_open())
 	{
 		cout<<"File in list1.txt NOT opened"<<endl;
 		return -1;
 	}

 	vector<TripletElements> StoryWordInfo;
	while (!documentList.eof() && documentList.good())
	{
		char buffer[512];
		documentList.getline(buffer, 512);
		string base = buffer;
		base = base.substr(0 , 15);
		string tripletsFilename = (pathTriplets + base +"_US_CNN_Newsroom.html.align.chunk_coref_triplets.dat");
		
		StoryWordInfo = cws.ReadTripletsFile(tripletsFilename);
		// cws.FirstSentAsTopic(tripletsFilename  , StoryTopicInfo);
	}

	//
	// Triplets classification
	//
	vector<TopicElements> StoryTopicInfo;
	vector<TopicElements> Story_InfoForTag;
	vector<TopicElements> Story_Tag_Info;
	vector<TopicElements> Resource_Goal_Tag;
	cws.ReadFullDocument(FILE_NEWSLIST, Story_InfoForTag);	
	cws.ReadTagFromFile(Story_InfoForTag);
	cws.ReadTagFromFile1(Story_Tag_Info);
	cws.ReadTag_Resource_Goal(Story_InfoForTag , Resource_Goal_Tag );
	cws.StoryTopic(Story_Tag_Info , StoryTopicInfo, Resource_Goal_Tag);


	vector<TripletElements> AllLongStories;
	cws.RemoveShortStory(StoryWordInfo ,  AllLongStories , RemovedStory);

	vector<StorySentInfo> storyNameAndSenNum ;
	cws.GetNumberOfStorySentence(AllLongStories , storyNameAndSenNum);

	vector<FinalTripletElements> StoryWordInfoFinal;
	cws.RemoveStopWords(AllLongStories ,  StoryWordInfoFinal, storyNameAndSenNum, 
				FILE_ANNA_JAR , FILE_ANNA_BEFORE_SPLIT , FILE_LEMMA_ENG_MODEL , FILE_ANNA_AFTER_SPLIT);
	cws.ExtractVocabularyList(StoryWordInfoFinal);
	cws.ParameterLearning(StoryWordInfoFinal , storyNameAndSenNum , FILE_ANNA_JAR, 
			__list_file9, __list_file10,
			__list_file11, __list_file12);


	// This is for similarity clustering :
	cws.CalculateSimilarity(StoryWordInfoFinal);
	//cws.TransitionMatrix_ScreenTopic(screenInfo);


  return 0;
}


//  cd /home/csa/CAS2/Arash/StoryTextInfo/
//  ./TextAnalysis /home/csa/CAS2/Arash/StoryTextInfo/ /home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/

//  argv[0] = /home/csa/CAS2/Arash/StoryTextInfo
//  java -Xmx1g -jar WNsim.jar n /home/csa/CAS2/Arash/StoryTextInfo/lemmatized_words.txt
