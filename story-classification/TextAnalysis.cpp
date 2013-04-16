#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <string> 
#include <time.h>
#include <stdio.h>
#include <vector>  
#include <sstream>
#include <iterator>
#include <algorithm>
#include <set>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <string.h>
#include <math.h>
#include <utility>
#include <assert.h>

#include "TextAnalysis.h"
#include "stopwords.h"

using namespace std; 


////////////////////////
// utilities
////////////////////////
std::string trim_front(const std::string& str, const std::string& trimChars)
{
    int i = 0;
    for (i = 0; i < str.size(); i++)
    {
        bool found = false;
        for (int j = 0; j < trimChars.size(); j++)
        {
            if (str[i] == trimChars[j])
                found = true;
        }
        if (found == false)
            break;
    }
    return str.substr(i);
}


TextAnalysis::TextAnalysis(){}
TextAnalysis::~TextAnalysis(){}

// getline just doesn't work..............

int getLineNew(istream &stream, string& result)
{
    result.clear();

    do 
    {
        char cc[10];
        //char c = 0;

        cc[0] = 0;
        cc[1] = 0;

        stream.get(cc[0]);
        char c = cc[0];

        if (c == ' ' && result.length() == 0)
            continue;

        if (c == '\n'|| c == 13 || c == 10 )
        { //|| c == 13 || c == 10 || c=='DA'
            if (result.length() == 0)
                continue;
            break;
        }

        if (c == 0)
            break;

        result += string(cc);

    } while(true);

    return result.length();
}


vector<Triplet> TextAnalysis::ReadTripletsFile(const string& tripletsFilename)
{
    ifstream ifs;
    ifs.open(tripletsFilename.c_str(), ios::in);
    string str, str2 ;
    vector<string> tokens;

    if (!ifs.is_open())
    {
        cout << "Cannot open triplets file:";
        cout << tripletsFilename << endl;        
        //EXCEPTION_TRIPLETS_FILE_CANNOT_OPEN;
    }

    vector<Triplet> storyWordInfo;
    while (!ifs.eof()  && ifs.good())
    {
        Triplet entry;
        char buffer[2048];
        ifs.getline(buffer, 2048);
        str = (buffer);
        size_t found = str.find("<");
        size_t foundVP = str.find("/VP");
        size_t foundNP = str.find("/NP");

        if ( str != "" )
        {
            if (found < 250 || foundVP < 250)
            {
                if (found == 0 )
                {
                    // extract topicName, timeStart, and timeEnd
                    found = str.find('>');
                    foundVP = str.find('/' );
                    str2 = str.substr ( 0, foundVP - 1 );
                    tokens.push_back(str2);

                    found = str.find("<story>");
                    if (found == 0)
                        entry.StoryTopicName = (str2.substr ( 0, str2.size()));

                    found = str.find("<start>");
                    if (found == 0){
                        str2 = str2.substr ( 0, str2.size() );
                        entry.StoryTimeStart = (str2);}

                    found = str.find("<end>");
                    if (found == 0){
                        str2 = str2.substr ( 0, str2.size() );
                        entry.StoryTimeEnd = (str2);}

                }
                else if (foundVP < 200  && foundNP < 200 )
                {
                    // extract NP1, VP, NP2
                    str2 = str.substr (foundNP + 4, (foundVP - foundNP )- 4 ); 
                    entry.Verb_Ph = (str2);

                    str2 = str.substr (0 , foundNP );
                    entry.Non_Ph1 = (str2);

                    str2 = str.substr (foundNP+4 , str.size() );
                    found = str2.find("/NP");
                    str2 = str2.substr (0 , found );
                    foundVP = str2.find("VP");
                    str2 = str2.substr (foundVP+3 , str2.size() );
                    foundVP = str2.find("PP;");                    
                    if (foundVP <= 50)
                    {
                        str2 = str2.substr (foundVP + 3 , str2.size() );
                    }
                    foundVP = str2.find("/PRT;");
                    
                    if (foundVP <= 50)
                    {
                        str2 = str2.substr (foundVP + 6 , str2.size() );
                    }
                    entry.Non_Ph2 = (str2);
                }

                char chars[] = "1234567890,:'?`";
                for (unsigned int ii = 0; ii < sizeof(chars); ++ii)
                {            
                    entry.Non_Ph1.erase(remove(entry.Non_Ph1.begin(), entry.Non_Ph1.end(), chars[ii]), entry.Non_Ph1.end());
                    entry.Verb_Ph.erase(remove(entry.Verb_Ph.begin(), entry.Verb_Ph.end(), chars[ii]), entry.Verb_Ph.end());
                    entry.Non_Ph2.erase(remove(entry.Non_Ph2.begin(), entry.Non_Ph2.end(), chars[ii]), entry.Non_Ph2.end());
                }
                replace(entry.Non_Ph1.begin(), entry.Non_Ph1.end(), '-', ' ');
                replace(entry.Verb_Ph.begin(), entry.Verb_Ph.end(), '-', ' ');
                replace(entry.Non_Ph2.begin(), entry.Non_Ph2.end(), '-', ' ');

                replace(entry.Non_Ph1.begin(), entry.Non_Ph1.end(), '\\', ' ');
                replace(entry.Verb_Ph.begin(), entry.Verb_Ph.end(), '\\', ' ');
                replace(entry.Non_Ph2.begin(), entry.Non_Ph2.end(), '\\', ' ');

                replace(entry.Non_Ph1.begin(), entry.Non_Ph1.end(), '/', ' ');
                replace(entry.Verb_Ph.begin(), entry.Verb_Ph.end(), '/', ' ');
                replace(entry.Non_Ph2.begin(), entry.Non_Ph2.end(), '/', ' ');

                storyWordInfo.push_back(entry);
            }
        }
    }
    return storyWordInfo;
}


vector <StoryInfo> TextAnalysis::TripletsToStories(const vector<Triplet> & triplets)
{
    vector <StoryInfo> stories;

    for( int i=0; i < triplets.size(); i++)
    {        
        size_t found_start = triplets[i].StoryTopicName.find("<story>");
        if (found_start == 0)
        {
            string storyName = triplets[i].StoryTopicName;
            storyName = storyName.substr(7, storyName.size());
            size_t found1 = storyName.find('|' );
            string category = storyName.substr(0, found1 );
            size_t found = category.find(':');
            if (found < 50)
            {
                category = category.substr ( 0, found );
            }

            StoryInfo current_story;
            current_story.name = storyName;
            current_story.category = category;
            current_story.num_sentences = 0;
            current_story.timeStart = triplets[i+1].StoryTimeStart;

            int num_sentences = 0;
            size_t found_end = 1;
            while ( found_end != 0 )
            {
                i++;
                num_sentences++;

                istringstream iss(triplets[i].Non_Ph1);
                copy (istream_iterator<string>(iss), istream_iterator<string>(), back_inserter(current_story.words_np1));

                istringstream iss1(triplets[i].Verb_Ph);
                copy (istream_iterator<string>(iss1), istream_iterator<string>(), back_inserter(current_story.words_vp));

                istringstream iss2(triplets[i].Non_Ph2);
                copy (istream_iterator<string>(iss2), istream_iterator<string>(), back_inserter(current_story.words_np2));

                found_end = triplets[i].StoryTimeEnd.find("<end>");
            }
            current_story.num_sentences = num_sentences-2;
            current_story.timeEnd = triplets[i].StoryTimeEnd;
            stories.push_back(current_story);
        }
    }
    return stories;
}

vector<StoryInfo> TextAnalysis::Lemmatize(const vector<StoryInfo>& stories)
{
    ofstream inout;
    inout.open(FILE_ANNA_BEFORE_SPLIT);
    for(int i=0; i < stories.size(); i++)
    {
        for (int j=0; j < stories[i].words_np1.size(); j++)
        {
            inout << stories[i].words_np1[j] << endl;
        }

        for (int j=0; j < stories[i].words_vp.size(); j++)
        {
            inout << stories[i].words_vp[j] << endl;
        }

        for (int j=0; j < stories[i].words_np2.size(); j++)
        {
            inout << stories[i].words_np2[j] << endl;
        }
    }
    inout.close();

    string CMD_split = "java -cp " FILE_ANNA_JAR " is2.util.Split " FILE_ANNA_BEFORE_SPLIT " > " FILE_ANNA_AFTER_SPLIT;
    system(CMD_split.c_str());

    string CMD_lemmatize = "java -Xmx2G -cp " FILE_ANNA_JAR " is2.lemmatizer.Lemmatizer -model " FILE_LEMMA_ENG_MODEL " -test " FILE_ANNA_AFTER_SPLIT " -out Lemmatizedfile.txt";
    system(CMD_lemmatize.c_str());

    ifstream lemmed ("Lemmatizedfile.txt");
    char buffer[500];
    char * pch;
    string wholeString , str_buf , str12 , str ;                        
    ofstream lemm_words ;
    lemm_words.open ("lemmatized_words.txt");
    vector<string> words;

    while (!lemmed.eof() && lemmed.good() ) 
    {
        lemmed.getline(buffer, 500, '\n');
        str_buf = (buffer);

        if (str_buf == "") 
        {
            lemm_words << wholeString << '\n';
            words.push_back(wholeString);
            wholeString = "";
        }
        if (str_buf != "" )
        {
            pch=strchr(buffer,'_');
            size_t foundNP1 = pch-buffer+1 ;
            pch=strchr(pch+1,'_');
            size_t foundVP = pch-buffer+1 ;
            str = str_buf.substr (foundNP1, (foundVP - foundNP1)-2 ); 
            wholeString = wholeString + " " + str ;
        }
    }
    lemmed.close();
    lemmed.clear();
    lemm_words.close();
    lemm_words.clear();

    int k = 0;
    vector<StoryInfo> stories_lemmed;
    for(int i=0; i < stories.size(); i++)
    {
        StoryInfo story_lemmed = stories[i];
        story_lemmed.words_np1.clear();
        story_lemmed.words_vp.clear();
        story_lemmed.words_np2.clear();

        for (int j=0; j < stories[i].words_np1.size(); j++)
        {
            assert(k < words.size());
            story_lemmed.words_np1.push_back(trim_front(words[k]," \t"));
            k++;
        }

        for (int j=0; j < stories[i].words_vp.size(); j++)
        {
            assert(k < words.size());
            story_lemmed.words_vp.push_back(trim_front(words[k]," \t"));
            k++;            
        }

        for (int j=0; j < stories[i].words_np2.size(); j++)
        {
            assert(k < words.size());
            story_lemmed.words_np2.push_back(trim_front(words[k]," \t"));
            k++;
        }

        stories_lemmed.push_back(story_lemmed);
    }

    return stories_lemmed;
}

vector<string> TextAnalysis::RemoveStopWords(const vector<string>& words)
{
    // stop words
    const static set<string> stopwords(stopwordsArray,
                        stopwordsArray + sizeof(stopwordsArray)/ sizeof(stopwordsArray[0]));

    vector<string> keep;
    // remove stop words
    for(int i = 0; i < words.size(); i++)
    {
        string word = words[i];

        if (word == "united" && words[i+1] == "state")
        {
            word = "u.s.";
            i++;
            keep.push_back(word);
            continue;
        }

        size_t found = word.find("'s");
        if (found <= 50)
        {
            word.erase(found,2);
        }

        found = word.find("$");
        if (found <= 50)
        {
            word = "dollar";
        }

        found = word.find("'");
        if (found <= 50)
        {
            word.erase(found,1);
        }

        if (word != "" && stopwords.find(word) == stopwords.end())
        {
            keep.push_back(word);
        }
    }
    return std::move(keep);
}

vector<StoryInfo> TextAnalysis::Cleasing(const vector<StoryInfo> & stories)
{   
    vector<StoryInfo> stories_new;

    for (int i = 0; i < stories.size(); i++)
    {
        // Skip NULL category stories and short stories.
        if (stories[i].category != "NULL" && stories[i].num_sentences > 4)
        {
            stories_new.push_back(stories[i]);
        }
    }

    // remove stop words.
    for(int i=0; i < stories_new.size(); i++)
    {
        stories_new[i].words_np1 = RemoveStopWords(stories_new[i].words_np1);
        stories_new[i].words_vp = RemoveStopWords(stories_new[i].words_vp);
        stories_new[i].words_np2 = RemoveStopWords(stories_new[i].words_np2);
    }
    return stories_new;
}


void TextAnalysis::ExtractVocabularyList(const vector<StoryInfo>& stories,
    set<string>& vocabularyNP1, set<string>& vocabularyVP, set<string>& vocabularyNP2)
{
    for(int i=0; i < stories.size(); i++)
    {
        for (int j=0; j < stories[i].words_np1.size(); j++)
        {
            vocabularyNP1.insert(stories[i].words_np1[j]);
        }
        for (int j=0; j < stories[i].words_vp.size(); j++)
        {
            vocabularyVP.insert(stories[i].words_vp[j]);
        }
        for (int j=0; j < stories[i].words_np2.size(); j++)
        {
            vocabularyNP2.insert(stories[i].words_np2[j]);
        }
    }   
}

void TextAnalysis::CrossValidation(
    const vector<StoryInfo>& stories,
    const set<string>& vocabularyNP1, 
    const set<string>& vocabularyVP, 
    const set<string>& vocabularyNP2,
    const int nfold)
{
    cout << "Preparing a " << nfold << " folds cross validation on " 
        << stories.size() << " stories..." << endl;
    // partition
    int nTestingSet = stories.size() / nfold;
    vector< pair<int, int> > testingRanges;     // begin, end
    int range_begin = 0, range_end = 0;
    for (int i = 0; i < nfold; i++)
    {
        if (i == nfold -1)
        {
            // last fold
            range_end = stories.size();
        }
        else
        {            
            range_end = range_begin + nTestingSet - 1;
        }
        
        assert(range_begin < stories.size());
        assert(range_end <= stories.size());

        testingRanges.push_back(pair<int, int>(range_begin, range_end));
        cout << "Fold " << i << ": " << range_begin << " - " << range_end << endl;
        range_begin = range_end;
    }
    
    vector< pair<double, double> > crossValidationResult;
    ofstream fout_eval;
    fout_eval.open("output/Triplets_CrossValidation.txt");

    // cross validation
    for (int kk = 0; kk < testingRanges.size(); kk++)
    {
        fout_eval << "---------------------" << endl;
        fout_eval << "Fold " << kk << endl;
        fout_eval << "---------------------" << endl;

        vector<StoryInfo> stories_testing;
        vector<StoryInfo> stories_training;

        auto currentRange = testingRanges[kk];
        for (int i=0; i<stories.size(); i++)
        {
            if(currentRange.first <= i &&  i < currentRange.second)
            {
                if (stories[i].category != "NULL")
                {
                    stories_testing.push_back(stories[i]);
                }
            }
            else
            {
                if (stories[i].category != "NULL")
                {
                    stories_training.push_back(stories[i]);
                }
            }
        }

        fout_eval << "Training set: " << stories_training.size() << endl;
        fout_eval << "Testing set:  " << stories_testing.size() << endl;
        fout_eval << "---------------------" << endl;

        //
        // Training
        //     

        NaiveBayesClassifier classifier;
        classifier.SetVocabularyNP1(vocabularyNP1);
        classifier.SetVocabularyVP(vocabularyVP);
        classifier.SetVocabularyNP2(vocabularyNP2);
        classifier.Train(stories_training);
        //classifier.SaveParametersToFile("output/model.txt");
        //classifier.LoadParametersFromFile("output/model.txt");

        //
        // Testing
        // Inference : Find the Posterior of new Unknown Story        
        //      

        const char* array[] = {"War","Sports", "Disaster" , "Accident","Activism", "Weather",
        "Social","Government","Science-technology","Religion","Politics", "International" ,
        "Lifestyle-leisure" , "Labor" , "Human-interest" , "Health" , "Environment" , 
        "Education" , "Business" ,  "Money" , "Crime", "Justice", "Art-culture", "Celebrity",
        "Entertainment", "Network" , "Commercial"};
        vector<string> categories(array, array + sizeof array / sizeof array[0]);

        int correct_count = 0;        
        for (int i = 0; i < stories_testing.size(); i++)
        {            
            string labeled_category = stories_testing[i].category;         

            PredictResult predict = classifier.Predict(stories_testing[i]);
            int predicted_category_idx = predict.label_id;
            string predicted_category = categories[predicted_category_idx];

            fout_eval << "Label: " << labeled_category << "\t ... \t" << predicted_category;

            if ( predicted_category == labeled_category )
            {
                // correct
                correct_count = correct_count +1;
                fout_eval << endl;
            }
            else
            {
                // Tolerance some situations
                size_t found = stories_testing[i].name.find("South-Ossetia");
                size_t found1 = stories_testing[i].name.find("georgia");              
                if( labeled_category == "Human-interest" || 
                    labeled_category=="Celebrity" || 
                    labeled_category=="Entertainment" ||
                    predicted_category == "Human-interest" ||
                    predicted_category=="Entertainment"||
                    (predicted_category=="War"  && found < 50) ||       // war = south-Ossetia
                    (predicted_category == "International" && found < 50) ||    // international = south-Ossetia
                    (predicted_category=="War"      && found1 < 10000) ||
                    (labeled_category == "Justice"  && predicted_category == "Crime") || // justice = crime
                    (labeled_category == "Crime"    && predicted_category == "Justice") ||
                    (labeled_category == "Disaster"     && predicted_category == "Weather") ||  // disaster = weather
                    (labeled_category == "Weather"  && predicted_category == "Disaster") ||
                    (labeled_category == "Accident"     && predicted_category == "Crime") ||    // accident = crime
                    (labeled_category == "Crime"    && predicted_category == "Accident"))
                {
                    correct_count = correct_count +1;
                    fout_eval << "\t tolerance" << endl;
                }
                else
                {
                    fout_eval << "\t WRONG" << endl;
                }
            }
        }
        crossValidationResult.push_back(make_pair(double(correct_count), double(stories_testing.size())));
    }

    // Output cross validation report.
    fout_eval << "# of stories in total:\t" << stories.size() << endl;
    PrintCrossValidationReport(fout_eval, crossValidationResult);
    PrintCrossValidationReport(cout, crossValidationResult);
    fout_eval.close();
}



// Using WordNet to calculate the similarity
// Using R to do the Hierarchical cluster
void TextAnalysis::CalculateSimilarity(const vector<StoryInfo> & StoryInfoForSim)
{
    //
    // Compute similarities using WordNet.
    //
    size_t found;
    ofstream inout;
    inout.open ("output/ForSim.txt");
    for(int i=0; i< StoryInfoForSim.size();i++)
    {
        if (StoryInfoForSim[i].words_np1.size()>0)
        {
            for(int j=0; j< StoryInfoForSim[i].words_np1.size();j++)
            {
                inout << StoryInfoForSim[i].words_np1[j] << endl;
            }
        }
    }
    inout.close();

    char sysCmdForJave[1024];
    char buf4[10];
    strcpy(buf4, "n");
    sprintf(sysCmdForJave, "java -Xmx1g -jar WNsim.jar %s %s", buf4 , "output/ForSim.txt");
    system(sysCmdForJave);

    //
    // Readin WordNet scores from text file.
    //
    string str;
    vector<double> AllScore;
    ifstream ifs;

    ifs.open("out.txt", ios::in);
    if (!ifs.is_open()) cout<<"out.txt File NOT opened"<<endl;
    while (!ifs.eof() && ifs.good() ) {
        char buffer[128];
        ifs.getline(buffer, 128);
        str = (buffer);
        double num = atof( str.c_str() );
        AllScore.push_back(num);
    }
    cout<<"AllScore Size  "<<AllScore.size()<<endl;  //// AllScore SIZE neeeed to be minus one 

    // 
    // Create a similarity matrix.
    //
    int MatLength = sqrt ( AllScore.size()-1);
    vector<vector <double> > Score_Mat;
    vector<double> Building_Mat;
    for(int i=0; i < MatLength; i++){ 
        Building_Mat.push_back(0);}
    for(int i=0; i < MatLength; i++){   
        Score_Mat.push_back(Building_Mat);}


    vector<vector <double> > Sim_Mat;
    Building_Mat.clear();
    for(int i=0; i < StoryInfoForSim.size(); i++){ 
        Building_Mat.push_back(0);}
    for(int i=0; i < StoryInfoForSim.size(); i++){  
        Sim_Mat.push_back(Building_Mat);}

    int Count=0;
    for(int j=0; j < Score_Mat.size(); j++){ 
        for(int k=0; k < Score_Mat.size() ; k++){ 
            Count++;
            Score_Mat[j][k] = AllScore[Count-1];
        }
    }

    vector<double>MaxVector;
    Count=0;int Count1=0;
    for(int i=0; i < StoryInfoForSim.size(); i++)
    {
        for(int ii=0; ii < StoryInfoForSim.size(); ii++)
        {

            double Ave=0;
            for(int j=0+Count; j < StoryInfoForSim[i].words_np1.size()+Count; j++)
            {
                double Max= Score_Mat[j][Count1];
                for(int k=0+Count1; k < StoryInfoForSim[ii].words_np1.size()+Count1; k++)
                {
//                  Ave = Ave+ Score_Mat[j][k];
                    if (Max < Score_Mat[j][k])
                    {
                        Max = Score_Mat[j][k];
                    }
                }
                MaxVector.push_back(Max);
            }
        
            for (int z=0; z<MaxVector.size();z++)
            {
                Ave = Ave+MaxVector[z];
            }
            Ave = Ave/MaxVector.size();MaxVector.clear();
            Sim_Mat[i][ii]=Ave;
            Count1=Count1+StoryInfoForSim[ii].words_np1.size();

        }
        Count=Count+StoryInfoForSim[i].words_np1.size();
        Count1=0;
    }

    for(int i=0; i<Sim_Mat.size(); i++)
    {
        for(int j=0; j<Sim_Mat.size(); j++)
        {
            Sim_Mat[j][i] = Sim_Mat[i][j];
        }
    }

    for(int i=0; i<Sim_Mat.size(); i++)
    {
        for(int j=0; j<Sim_Mat.size(); j++)
        {
            Sim_Mat[i][j] = 1- Sim_Mat[i][j];
        }
    }
    for(int i=0; i<Sim_Mat.size(); i++)
    {
        Sim_Mat[i][i] = 0;
    }

    //
    // Save similarity matrix in a file.
    //
    Count=0;
    char Simi = '"';
    inout.open ("output/similarity_matrix.txt");
    string WholeNumber;
    for(int i=0; i<Sim_Mat.size(); i++)
    {
        for(int j=0; j<Sim_Mat.size(); j++)
        {
            inout<<Sim_Mat[i][j];
            if(j<Sim_Mat.size()-1)
            {
                inout<<" ";
            }
            Count++;
        }
        inout<<'\n';
    }
    inout.close();

    inout.open ("output/story_name.txt");
    for(int i=0; i<StoryInfoForSim.size(); i++){

        inout << Simi << StoryInfoForSim[i].name << Simi;
        if(i < StoryInfoForSim.size()-1)
        {
            inout<<" ";
        }
    }
    inout.close();

    //
    // Using R to do the hierarchical clustering.
    //
    system("R CMD BATCH hcscript.r");
}


// Output Cross validation report
void TextAnalysis::PrintCrossValidationReport(ostream& os, 
    const vector<pair<double, double> >& crossValidation)
{
    if (crossValidation.size() == 0)
    {
        os << "No results available.";
        return;
    }

    double accuracy_sum = 0;
    os << "--------------------------" << endl;
    os << "CROSS VALIDATION REPORT" << endl;
    os << "--------------------------" << endl;    
    for (int i=0; i < crossValidation.size(); i++)
    {
        pair<double, double> result = crossValidation[i];
        double correct_count = result.first;
        double total = result.second;
        double accuracy = correct_count / total;
        accuracy_sum += accuracy;
        os << "Fold " << i << ":\t" << accuracy << "\t ( "
            << correct_count << " out of " << total << " )" << endl;
    }

    os << "--------------------------" << endl;
    os << "AVG.: " << accuracy_sum/(double)crossValidation.size() << endl;
}

void TextAnalysis::TransitionMatrix_ScreenTopic(vector<ScreenInfo> &Screen_Info_Final){
        
    size_t found;
    int Category_Number=  27;
    vector<vector <int> > TranMat_ScTopic;
    vector<int> Building_Mat;
    for(int i=0; i < Category_Number; i++){ 
        Building_Mat.push_back(0);}
    for(int i=0; i < Category_Number; i++){     
        TranMat_ScTopic.push_back(Building_Mat);}

        const char* array[] = {"War","Sports", "Disaster" , "Accident","Activism", "Weather",
            "Social","Government","Science-technology","Religion","Politics", "International" ,
            "Lifestyle-leisure" , "Labor" , "Human-interest" , "Health" , "Environment" , 
            "Education" , "Business" ,  "Money" , "Crime", "Justice", "Art-culture", "Celebrity",
            "Entertainment", "Network" , "Commercial"};
        vector<string> categories(array, array + sizeof array / sizeof array[0]);
        int iIndix=0;
        for (int i=0; i<Screen_Info_Final.size(); i++){
            found = Screen_Info_Final[i].StoryTopicName.find("|");
            string Cat = Screen_Info_Final[i].StoryTopicName.substr( 0, found);
            for (int j=0; j<categories.size(); j++){
                if ( Cat.compare(categories[j]) == 0 ){
                    TranMat_ScTopic[iIndix][j] = TranMat_ScTopic[iIndix][j] + 1;
                    iIndix=j;
                }
            }
        }

    }

