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
        pathRoot = argv[1];     //   /home/csa/CAS2/Arash/StoryTextInfo/   
        pathTriplets = argv[2]; //   /home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/
    }
    */

    TextAnalysis cws;    
    vector<int> RemovedStory;

    //// This part for Russian news article :
    // vector<TopicElements> ArticleTopicInfo;
    // cws.TopicOnWebArticle(ArticleTopicInfo , list_file4 , list_file2);

    //
    // OCR classification
    //
    /*
    vector<ScreenInfo> screenInfo;
    set<string> screen_vocabulary;

    cout << "OCR loading..." << endl;
    cws.Screen_Text_Info(screenInfo, screen_vocabulary, DIR_OCR,
        DIR_ANNOTATEDTEXT, FILE_NEWSLIST);
    //cws.Generate_Reference_Vocabulary();
    screenInfo = cws.RemoveShortStory_ScreenTopic(screenInfo, RemovedStory);

    cout << "OCR cross validation..." << endl;
    cws.ParameterLearning_ScreenTopic(screenInfo, screen_vocabulary);
    */
    
    //
    // Triplets classification
    //
    ifstream documentList;
    documentList.open(FILE_NEWSLIST, ios::in);
    if (!documentList.is_open())
    {
        cout<<"News list cannot be opened."<<endl;
        return -1;
    }

    cout << "Triplets loading..." << endl;
    vector<Triplet> storyWordInfo;
    while (!documentList.eof() && documentList.good())
    {
        char buffer[512];
        documentList.getline(buffer, 512);
        string base = buffer;
        base = base.substr(0 , 15);
        string tripletsFilename = (pathTriplets + base +"_US_CNN_Newsroom.html.align.chunk_coref_triplets.dat");
        vector<Triplet> temp = cws.ReadTripletsFile(tripletsFilename);
        storyWordInfo.insert(storyWordInfo.end(), temp.begin(), temp.end());
        // cws.FirstSentAsTopic(tripletsFilename, StoryTopicInfo);
    }

    /* 
    vector<TopicElements> StoryTopicInfo;
    vector<TopicElements> storyInfoForTag = cws.ReadFullDocument(FILE_NEWSLIST);
    cws.ReadTagFromFile(storyInfoForTag);
    vector<TopicElements> storyInfoTags = cws.ReadTagFromFile1();   
    vector<TopicElements> resourceGoalTags = cws.ReadTag_ResourceGoal(storyInfoForTag);
    cws.StoryTopic(storyInfoTags , StoryTopicInfo, resourceGoalTags);
    */


    cout << "Triplets remove short stories..." << endl;
    vector<Triplet> longStories = cws.RemoveShortStory(storyWordInfo, RemovedStory);
    vector<StorySentInfo> storyNameAndSenNum = cws.GetNumberOfStorySentence(longStories);

    cout << "Remove stop words..." << endl;
    
    vector<FinalTriplet> storyWordInfoFinal = cws.RemoveStopWords(
        longStories, storyNameAndSenNum);

    cout << "Extract vocabulary..." << endl;

    set<string> vocabularyNP1, vocabularyVP, vocabularyNP2;
    cws.ExtractVocabularyList(storyWordInfoFinal,
        vocabularyNP1, vocabularyVP, vocabularyNP2);
    
    vector<StoryInfo> stories = cws.GetStories(storyWordInfoFinal);
    // Train model
    cout << "Training Model..." << endl;
    NaiveBayesClassifier classifier;
    classifier.SetVocabularyNP1(vocabularyNP1);
    classifier.SetVocabularyVP(vocabularyVP);
    classifier.SetVocabularyNP2(vocabularyNP2);
    classifier.Train(stories);
    classifier.SaveParametersToFile("output/model.txt");

    cout << "Triplets validation..." << endl;
    //cws.CrossValidation(
    //    stories, vocabularyNP1, vocabularyVP, vocabularyNP2);

    // Clustering based on NP1 similarities.    
    //cws.CalculateSimilarity(stories);

    ////cws.TransitionMatrix_ScreenTopic(screenInfo);

  return 0;
}

//  ./TextAnalysis /home/csa/CAS2/Arash/StoryTextInfo/ /home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/

//  argv[0] = /home/csa/CAS2/Arash/StoryTextInfo
//  java -Xmx1g -jar WNsim.jar n /home/csa/CAS2/Arash/StoryTextInfo/lemmatized_words.txt