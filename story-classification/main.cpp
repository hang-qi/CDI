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
#include "segmenter.h"
#pragma comment(lib, "User32.lib")
using namespace std; 

int main(int argc, const char* argv[])
{
    enum Option
    {
        NONE,
        CLASSIFIER_TRAIN,
        CLASSIFIER_PREDICT,
        CLASSIFIER_VALIDATE,
        SEGMENTATION_TRAIN,
        SEGMENTATION_PREDICT
    };

    Option opt = NONE;
    //string targetfiles;
    
    // .TextAnalysis [--train|--validation|--predict] file      
    if (argc == 2)
    {
        if (string(argv[1]) == "--train")
        {
            opt = CLASSIFIER_TRAIN;
        }
        else if(string(argv[1]) == "--predict")
        {
            opt = CLASSIFIER_PREDICT;
        }        
        else if(string(argv[1]) == "--validate")
        {
            opt = CLASSIFIER_VALIDATE;
        }
        else if(string(argv[1]) == "--seg-train")
        {
            opt = SEGMENTATION_TRAIN;
        }
        else if(string(argv[1]) == "--seg-predict")
        {
            opt = SEGMENTATION_PREDICT;
        }
        else
        {
            cout << "Unknown command." << endl;
            return -1;
        }
        //targetfiles = argv[2];
        //cout << targetfiles << endl;
    }
    else
    {
        cout << "Unknown command." << endl;
        return -1;
    }

    string pathTriplets = "/home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/";
    /*if (argc == 3)
    {
        pathRoot = argv[1];     //   /home/csa/CAS2/Arash/StoryTextInfo/   
        pathTriplets = argv[2]; //   /home/csa/CAS2/wang296/Projects/tSegment/Data/Triplets/coreNLP/
    }
    */

    TextAnalysis cws;
    
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

    if (opt == CLASSIFIER_TRAIN)
    {
        // Train model
        cout << "Training Model..." << endl;
        NaiveBayesClassifier classifier;
        classifier.Train(stories, 27);
        classifier.Save("output/model.txt");
    }
    else if (opt == CLASSIFIER_VALIDATE)
    {
        cout << "Triplets validation..." << endl;
        cws.CrossValidation(stories);
    }
    else if (opt == CLASSIFIER_PREDICT)
    {
        // Predict by default
        NaiveBayesClassifier classifier("output/model.txt");
        for (int i = 0; i < stories.size(); i++)
        {
            PredictResult result = classifier.Predict(stories[i]);            
        }
    }
    else if (opt == SEGMENTATION_TRAIN)
    {
        Segmenter segmenter;
        segmenter.Train(stories, 27);
        segmenter.Save("output/model_segmenter.txt");
    }
    else if (opt == SEGMENTATION_PREDICT)
    {
        Segmenter segmenter("output/model_segmenter.txt");
        segmenter.SegmentStories(stories);
    }

    // Clustering based on NP1 similarities.    
    //cws.CalculateSimilarity(stories);

  return 0;
}
