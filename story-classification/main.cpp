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
    bool isTraining = false;
    bool isValidation = false;
    string targetfiles;
    
    // .TextAnalysis [--train|--validation|--predict] file
    vector<string> args;
    for (int i =0; i < argc; i++)
    {
        args.push_back(argv[i]);
    }
    
    if (args.size() == 3)
    {
        if (args[1] == "--train")
        {
            isTraining = true;
        }
        else if(args[1] == "--predict")
        {
            isTraining = false;
            isValidation = false;
        }        
        else if(args[1] == "--validation")
        {
            isValidation = true;
        }
        else
        {
            cout << "Unknown command." << endl;
            return -1;
        }
        targetfiles = argv[2];
        cout << targetfiles << endl;
    }

    string pathTriplets = "/home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/";
    /*if (argc == 3)
    {
        pathRoot = argv[1];     //   /home/csa/CAS2/Arash/StoryTextInfo/   
        pathTriplets = argv[2]; //   /home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/
    }
    */

    TextAnalysis cws;    
    vector<int> RemovedStory;   
    
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
    vector<StoryInfo> stories;
    int document_id = 0;
    while (!documentList.eof() && documentList.good())
    {
        char buffer[512];
        documentList.getline(buffer, 512);
        string base = buffer;
        base = base.substr(0 , 15);
        string tripletsFilename = (pathTriplets + base +"_US_CNN_Newsroom.html.align.chunk_coref_triplets.dat");        
        vector<Triplet> triplets = cws.ReadTripletsFile(tripletsFilename);        
        vector<StoryInfo> tmp_stories = cws.TripletsToStories(triplets);
        for (int i = 0; i < tmp_stories.size(); i++)
        {
            tmp_stories[i].document_id = document_id;
        }
        stories.insert(stories.end(), tmp_stories.begin(), tmp_stories.end());        
        document_id++;

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

    stories = cws.Lemmatize(stories);
    stories = cws.Cleasing(stories);
    // remove short stories
    // remove stop words

    //vector<Triplet> longStories = cws.RemoveShortStory(storyWordInfo, RemovedStory);
    //vector<StorySentInfo> storyNameAndSenNum = cws.GetNumberOfStorySentence(longStories);
    
    //vector<FinalTriplet> storyWordInfoFinal = cws.RemoveStopWords(
    //    longStories, storyNameAndSenNum);

    //vector<StoryInfo> stories = cws.GetStories(storyWordInfoFinal);

    set<string> vocabularyNP1, vocabularyVP, vocabularyNP2;
    cws.ExtractVocabularyList(stories,
        vocabularyNP1, vocabularyVP, vocabularyNP2);

    exit(0);

    if (isTraining)
    {
        // Train model
        cout << "Training Model..." << endl;
        NaiveBayesClassifier classifier;
        classifier.SetVocabularyNP1(vocabularyNP1);
        classifier.SetVocabularyVP(vocabularyVP);
        classifier.SetVocabularyNP2(vocabularyNP2);
        classifier.Train(stories);
        classifier.SaveParametersToFile("output/model.txt");
    }
    else if(isValidation)
    {
        cout << "Triplets validation..." << endl;
        cws.CrossValidation(
            stories, vocabularyNP1, vocabularyVP, vocabularyNP2);
    }
    else
    {
        // Predict by default
        NaiveBayesClassifier classifier;
        classifier.LoadParametersFromFile("output/model.txt");
    }

    // Clustering based on NP1 similarities.    
    //cws.CalculateSimilarity(stories);

    ////cws.TransitionMatrix_ScreenTopic(screenInfo);

  return 0;
}

//  ./TextAnalysis /home/csa/CAS2/Arash/StoryTextInfo/ /home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/

//  argv[0] = /home/csa/CAS2/Arash/StoryTextInfo
//  java -Xmx1g -jar WNsim.jar n /home/csa/CAS2/Arash/StoryTextInfo/lemmatized_words.txt


    // OCR classification
    //
    /*
    vector<ScreenInfo> screenInfo;
    set<string> screen_vocabulary;

    cout << "OCR loading..." << endl;
    cws.Screen_Text_Info(screenInfo, screen_vocabulary, DIR_OCR,
        DIR_ANNOTATEDTEXT, FILE_NEWSLIST);
    screenInfo = cws.RemoveShortStory_ScreenTopic(screenInfo, RemovedStory);

    cout << "OCR cross validation..." << endl;
    cws.ParameterLearning_ScreenTopic(screenInfo, screen_vocabulary);
    */