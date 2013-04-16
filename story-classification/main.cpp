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
    //string targetfiles;
    
    // .TextAnalysis [--train|--validation|--predict] file      
    if (argc == 2)
    {
        if (string(argv[1]) == "--train")
        {
            isTraining = true;
        }
        else if(string(argv[1]) == "--predict")
        {
            isTraining = false;
            isValidation = false;
        }        
        else if(string(argv[1]) == "--validation")
        {
            isValidation = true;
        }
        else
        {
            cout << "Unknown command." << endl;
            return -1;
        }
        //targetfiles = argv[2];
        //cout << targetfiles << endl;
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
    }
    
    // remove stop words
    stories = cws.Lemmatize(stories);
    stories = cws.Cleasing(stories);

    if (isTraining)
    {
        // Train model
        cout << "Training Model..." << endl;
        NaiveBayesClassifier classifier;
        classifier.Train(stories, 27);
        classifier.SaveParametersToFile("output/model.txt");
    }
    else if(isValidation)
    {
        cout << "Triplets validation..." << endl;
        cws.CrossValidation(stories);
    }
    else
    {
        // Predict by default
        NaiveBayesClassifier classifier;
        classifier.LoadParametersFromFile("output/model.txt");
        for (int i = 0; i < stories.size(); i++)
        {
            PredictResult result = classifier.Predict(stories[i]);            
        }
    }

    // Clustering based on NP1 similarities.    
    //cws.CalculateSimilarity(stories);

    ////cws.TransitionMatrix_ScreenTopic(screenInfo);

  return 0;
}
