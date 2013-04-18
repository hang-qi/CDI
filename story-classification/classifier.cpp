#include <assert.h>

#include "classifier.h"
#include "utility.h"

#define SMALL_NUM 1.5e-100

void NBClassifierParameter::Serialize(ostream& os) const
{
    os << num_categories << endl;
    os << vocabulary_np1 << endl;
    os << vocabulary_vp << endl;
    os << vocabulary_np2 << endl;
    os << priors_cat << endl;
    os << prob_wordsGivenCatsNP1 << endl;
    os << prob_wordsGivenCatsVP << endl;
    os << prob_wordsGivenCatsNP2 << endl;
}

void NBClassifierParameter::Unserialize(istream& is)
{
    is >> num_categories;
    is >> vocabulary_np1;
    is >> vocabulary_vp;
    is >> vocabulary_np2;
    is >> priors_cat;
    is >> prob_wordsGivenCatsNP1;
    is >> prob_wordsGivenCatsVP;
    is >> prob_wordsGivenCatsNP2;
}

PredictResult NaiveBayesClassifier::Predict(const StoryFeature& storyfeature) const
{
    // Calculate P(Cat|NP1)  P(Cat|VP)  P(Cat|NP2)
    vector<double> dist_catGivenNP1 = CalcualtePostProbCats(
       storyfeature.wordIds_np1, param_.prob_wordsGivenCatsNP1);

    vector<double> dist_catGivenVP = CalcualtePostProbCats(
       storyfeature.wordIds_vp, param_.prob_wordsGivenCatsVP);

    vector<double> dist_catGivenNP2 = CalcualtePostProbCats(
       storyfeature.wordIds_np2, param_.prob_wordsGivenCatsNP2);


    vector<double> dist_catGivenStory;
    for (int i=0; i < param_.num_categories; i++)
    {
        double A = dist_catGivenNP1[i] * dist_catGivenVP[i] * dist_catGivenNP2[i];
        A = A / (param_.priors_cat[i] * param_.priors_cat[i]);
        dist_catGivenStory.push_back(A);
    }

    // dist_catGivenStory = utility::Normalize(dist_catGivenStory);
    
    // Predict by the maximum posterior probability (Bayes Decision).
    int predicted_category_idx = max_element(dist_catGivenStory.begin(), dist_catGivenStory.end()) - dist_catGivenStory.begin();
    
    PredictResult result;
    result.label_id = predicted_category_idx;
    result.joint_prob = dist_catGivenStory[predicted_category_idx];
    return result;
}

PredictResult NaiveBayesClassifier::Predict(const StoryInfo& story) const
{
    StoryFeature storyfeature = ConvertStoryToFeature(story);
    return Predict(storyfeature);
}

// calculate prior probability for each category.
// P(cat)
//
vector<double> NaiveBayesClassifier::CalculatePriors(
    const vector<StoryInfo>& labeled_stories)
{    
    vector<double> prob_cat(param_.num_categories);

    // count
    for (int i =0; i < labeled_stories.size(); i++)
    {
        assert(labeled_stories[i].category_id >=0 
            && labeled_stories[i].category_id < param_.num_categories);
        prob_cat[labeled_stories[i].category_id]++;
    }    
    
    // normalize    
    for(int i = 0; i < prob_cat.size(); i++)
    {
        prob_cat[i] = prob_cat[i] / double(labeled_stories.size());
    }
    return prob_cat;
}

NBClassifierParameter NaiveBayesClassifier::Train(const vector<StoryInfo>& labeled_stories, int num_categories)
{
    
    ExtractVocabulary(labeled_stories);

    vector<double> prob_cat = CalculatePriors(labeled_stories);
    int num_stories = labeled_stories.size();

    // Building co-occurrence of (words given cat) AND P(Wi | Catj)
    Matrix WordsCatMatrixNP1 = utility::BuildMatrix(param_.vocabulary_np1.size(), num_categories);
    Matrix WordsCatMatrixVP = utility::BuildMatrix(param_.vocabulary_vp.size(), num_categories);        
    Matrix WordsCatMatrixNP2 = utility::BuildMatrix(param_.vocabulary_np2.size(), num_categories);
        
    // (words Given Stories)
    Matrix WordsStoriesMatrixNP1 = utility::BuildMatrix(param_.vocabulary_np1.size(), num_stories);
    Matrix WordsStoriesMatrixVP = utility::BuildMatrix(param_.vocabulary_vp.size(), num_stories);
    Matrix WordsStoriesMatrixNP2 = utility::BuildMatrix(param_.vocabulary_np2.size(), num_stories);

    int NumberOfAllWordsInDocument=0;     
    
    vector<string>& v = param_.vocabulary_np1;
    vector<string>& v1 = param_.vocabulary_vp;
    vector<string>& v2 = param_.vocabulary_np2;

    vector<int> counts_np1;
    vector<int> counts_vp;
    vector<int> counts_np2;

    // fill in WordCatMatrix and WordsStoryMatrix     
    for (int story_id = 0; story_id < labeled_stories.size(); story_id++)
    {
        const StoryInfo& current_story = labeled_stories[story_id];        

        int category_id = current_story.category_id;
        assert(category_id != -1);

        // Non_Ph1
        for(int i=0; i < current_story.words_np1.size(); i++)
        {                           
            int word_id = FindWordId(v, current_story.words_np1[i]);
            assert(word_id >= 0);                
            if (word_id < v.size() )
            {
                WordsCatMatrixNP1[word_id][category_id] += 1;
                WordsStoriesMatrixNP1[word_id][story_id] += 1;
            }
        }        
        counts_np1.push_back(current_story.words_np1.size());

        // Verb_ph
        for(int i=0; i < current_story.words_vp.size(); i++)
        {
            int word_id = FindWordId(v1, current_story.words_vp[i]);
            assert(word_id >= 0);
            if (word_id < v1.size() )
            {
                WordsCatMatrixVP[word_id][category_id] += 1;
                WordsStoriesMatrixVP[word_id][story_id] += 1;
            }
        }
        counts_vp.push_back(current_story.words_vp.size());

        // Non_ph2
        for(int i=0; i < current_story.words_np2.size(); i++)
        {                           
            int word_id = FindWordId(v2, current_story.words_np2[i]);
            assert(word_id >= 0);
            if (word_id < v2.size() )
            {
                WordsCatMatrixNP2[word_id][category_id] += 1;
                WordsStoriesMatrixNP2[word_id][story_id] += 1;
            }
        }
        counts_np2.push_back(current_story.words_np2.size());
    }


    //
    // counts of NP1, VP, NP2
    //
    vector<double> prob_storylen;
    vector<double> prob_storylen1;
    vector<double> prob_storylen2;

    for (int i=0; i< counts_np1.size(); i++ )
    {
        double NumOfEqualStory=0;
        for (int j=0; j< counts_np1.size(); j++ )
        {
            if (counts_np1[i] == counts_np1[j])
            {
                NumOfEqualStory = NumOfEqualStory+1;
            }
        }
        double StoryProb = NumOfEqualStory/counts_np1.size();
        prob_storylen.push_back(StoryProb);
    }

    for (int i=0; i< counts_vp.size(); i++ ){
        double NumOfEqualStory=0;
        for (int j=0; j< counts_vp.size(); j++ ){
            if (counts_np1[i] == counts_np1[j]){
                NumOfEqualStory = NumOfEqualStory+1;
            }
        }
        double StoryProb = NumOfEqualStory/counts_vp.size();
        prob_storylen1.push_back(StoryProb);
    }

    for (int i=0; i< counts_np2.size(); i++ ){
        double NumOfEqualStory=0;
        for (int j=0; j< counts_np2.size(); j++ ){
            if (counts_np2[i] == counts_np2[j]){
                NumOfEqualStory = NumOfEqualStory+1;
            }
        }
        double StoryProb = NumOfEqualStory/counts_np2.size();
        prob_storylen2.push_back(StoryProb);
    }

    //
    // Calculating P(Wi|Catj)^time (Np1,Vp.Np2) and save it in WordsCatMatrixNP1,WordsCatMatrixVP,WordsCatMatrixNP2 
    //
    Matrix prob_wordsGivenCatsNP1 = utility::Normalize2D(WordsCatMatrixNP1);
    Matrix prob_wordsGivenCatsVP = utility::Normalize2D(WordsCatMatrixVP);
    Matrix prob_wordsGivenCatsNP2 = utility::Normalize2D(WordsCatMatrixNP2);

    //Building The Probability of Story Given Category  P(Si|Catj)^time  for NP1,VP,NP2
    // Building P(Si | Catj) AND P(Catj | Si)        
    Matrix ProbStoryGivenCat = utility::BuildMatrix(num_stories, num_categories);
    Matrix ProbStoryGivenCat1 = utility::BuildMatrix(num_stories, num_categories);
    Matrix ProbStoryGivenCat2 = utility::BuildMatrix(num_stories, num_categories);

    Matrix ProbCatGivenStory = utility::BuildMatrix(num_stories, num_categories);
    Matrix ProbCatGivenStory1 = utility::BuildMatrix(num_stories, num_categories);
    Matrix ProbCatGivenStory2 = utility::BuildMatrix(num_stories, num_categories);   

    vector<int> AllCountedWordsInStories;
    vector<int> AllCountedWordsInStories1;
    vector<int> AllCountedWordsInStories2;

    for (int story_id = 0; story_id < labeled_stories.size(); story_id++)
    {
        const StoryInfo& current_story = labeled_stories[story_id];

        int category_id = current_story.category_id;

        vector<double> prob_wordsNP1InStoryGivenCat;
        vector<double> prob_wordsVPInStoryGivenCat;
        vector<double> prob_wordsNP2InStoryGivenCat;
        
        int num_wordsNP1 = 0, num_wordsVP = 0, num_wordsNP2 = 0;
        
        // NP1
        for(int k=0; k < current_story.words_np1.size(); k++)
        {
            auto low = lower_bound (v.begin(), v.end(), current_story.words_np1[k]);
            string WordName = *low;
            if(WordName == current_story.words_np1[k])
            {
                int word_id = int(low- v.begin());
                double prob_word = 0;
                if (word_id < v.size() )
                {                                    
                    prob_word = prob_wordsGivenCatsNP1[word_id][category_id];
                    num_wordsNP1++;
                }
                prob_wordsNP1InStoryGivenCat.push_back(prob_word);
            }
        }

        for(int k=0; k < current_story.words_vp.size(); k++)
        {
            auto low = lower_bound (v1.begin(), v1.end(), current_story.words_vp[k]);
            string WordName = *low;             
            if(WordName == current_story.words_vp[k])
            {
                int word_id = int(low- v1.begin());                                    
                double prob_word = 0;
                if (word_id < v1.size() )
                {                                
                    prob_word = prob_wordsGivenCatsVP[word_id][category_id];
                    num_wordsVP++;
                }
                prob_wordsVPInStoryGivenCat.push_back(prob_word);
            }
        }

        // NP2
        for(int k=0; k < current_story.words_np2.size(); k++)
        {
            auto low = lower_bound (v2.begin(), v2.end(), current_story.words_np2[k]);
            string WordName = *low;             
            if(WordName == current_story.words_np2[k])
            {
                int word_id = int(low- v2.begin());                                    
                double prob_word = 0;
                if (word_id < v2.size() )
                {                                
                    prob_word = prob_wordsGivenCatsNP2[word_id][category_id];
                    num_wordsNP2++;
                }
                prob_wordsNP2InStoryGivenCat.push_back(prob_word);
            }
        }
                    
        AllCountedWordsInStories.push_back(num_wordsNP1);
        AllCountedWordsInStories1.push_back(num_wordsVP);
        AllCountedWordsInStories2.push_back(num_wordsNP2);

        // Calculate probability of story
        double prob_OneStorygivnCat = 1;
        for (int k = 0; k < prob_wordsNP1InStoryGivenCat.size(); k++)
        {
            prob_OneStorygivnCat *= prob_wordsNP1InStoryGivenCat[k];
        }

        if (prob_OneStorygivnCat < SMALL_NUM)
        {
            ProbStoryGivenCat[story_id][category_id] = SMALL_NUM;
        }
        else
        {
            ProbStoryGivenCat[story_id][category_id] = prob_OneStorygivnCat * prob_storylen[story_id];
        }
        /////

        prob_OneStorygivnCat = 1;
        for (int kk = 0; kk < prob_wordsVPInStoryGivenCat.size(); kk++)
        {
            prob_OneStorygivnCat *= prob_wordsVPInStoryGivenCat[kk];
        }
        if (prob_OneStorygivnCat < SMALL_NUM)
        {
            ProbStoryGivenCat1[story_id][category_id] = SMALL_NUM;
        }
        else
        {
            ProbStoryGivenCat1[story_id][category_id] = prob_OneStorygivnCat * prob_storylen1[story_id];
        }
        //////
                          
        prob_OneStorygivnCat = 1;
        for (int kk = 0; kk < prob_wordsNP2InStoryGivenCat.size(); kk++)
        {
            prob_OneStorygivnCat *= prob_wordsNP2InStoryGivenCat[kk];
        }                    
        if (prob_OneStorygivnCat < SMALL_NUM )
        {
            ProbStoryGivenCat2[story_id][category_id] = SMALL_NUM;
        }
        else
        {
            ProbStoryGivenCat2[story_id][category_id] = prob_OneStorygivnCat * prob_storylen2[story_id];
        }
    } 

        // Normalizing of the ProbStoryGivenCat which gives Probability of Story Given Category:P(Si|Catj)^time
    ProbStoryGivenCat = utility::Normalize2D(ProbStoryGivenCat);
    ProbStoryGivenCat1 = utility::Normalize2D(ProbStoryGivenCat1);
    ProbStoryGivenCat2 = utility::Normalize2D(ProbStoryGivenCat2);

    vector<double> prob_Story(num_stories);
    vector<double> prob_Story1(num_stories);
    vector<double> prob_Story2(num_stories);

    for (int i=0; i<num_stories; i++)
    {
        // p(story_i) = \sum_{cat_j} p(story_i | category_j) * p(cat_j)
        double prob = 0, prob1 = 0, prob2 = 0;
        for(int j=0; j< num_categories; j++)
        {
            prob += prob_cat[j]*ProbStoryGivenCat[i][j];
            prob1 += prob_cat[j]*ProbStoryGivenCat1[i][j];
            prob2 += prob_cat[j]*ProbStoryGivenCat2[i][j];
        }
        prob_Story[i] = prob;
        prob_Story1[i] = prob1;
        prob_Story2[i] = prob2;
    }

    //
    // Starting Iteration for EM - Algorithm
    //

    // E_Step: 
       // Building The Probability of Category Given Story P(Catj|Si)^(t+1)   t=time  FOR NP1,VP,NP2
    for (int i=0; i<num_stories; i++)
    {
        for (int j=0; j< num_categories; j++)
        {
            ProbCatGivenStory[i][j] = prob_cat[j]*ProbStoryGivenCat[i][j]/prob_Story[i];
            ProbCatGivenStory1[i][j] = prob_cat[j]*ProbStoryGivenCat1[i][j]/prob_Story1[i];
            ProbCatGivenStory2[i][j] = prob_cat[j]*ProbStoryGivenCat2[i][j]/prob_Story2[i];
        }
    }

        // M_Step: 
        // Updating The Probability of Each Words in vocabulary Given Category    
        // P(Wn|Catj)^(t+1)   t=time

    for (int i=0; i<v.size(); i++)
    {
        for (int j=0; j< num_categories; j++)
        {
            double Numeratorwithoutsmooth = 0;
            double DeNumeratorwithoutsmooth = 0;
            for (int k=0; k<num_stories; k++)
            {
                Numeratorwithoutsmooth += ProbCatGivenStory[k][j]*WordsStoriesMatrixNP1[i][k];
                DeNumeratorwithoutsmooth += ProbCatGivenStory[k][j]*AllCountedWordsInStories[k]; 
            }
            prob_wordsGivenCatsNP1[i][j] = (1 + Numeratorwithoutsmooth) / (v.size() + DeNumeratorwithoutsmooth);
        }
    }

    for (int i=0; i<v1.size(); i++)
    {
        for (int j=0; j< num_categories; j++)
        {
            double Numeratorwithoutsmooth = 0;
            double DeNumeratorwithoutsmooth = 0;
            for (int k=0; k<num_stories; k++){
            Numeratorwithoutsmooth += ProbCatGivenStory1[k][j]*WordsStoriesMatrixVP[i][k];
            DeNumeratorwithoutsmooth += ProbCatGivenStory1[k][j]*AllCountedWordsInStories[k];    
            }
            prob_wordsGivenCatsVP[i][j] = (1 + Numeratorwithoutsmooth) / (v1.size() + DeNumeratorwithoutsmooth);
        }
    }

    for (int i=0; i<v2.size(); i++)
    {
        for (int j=0; j< num_categories; j++)
        {
            double Numeratorwithoutsmooth = 0;
            double DeNumeratorwithoutsmooth = 0;
            for (int k=0; k<num_stories; k++){
            Numeratorwithoutsmooth += ProbCatGivenStory2[k][j]*WordsStoriesMatrixNP2[i][k];
            DeNumeratorwithoutsmooth  += ProbCatGivenStory2[k][j]*AllCountedWordsInStories[k];
            //cout<< "[k][j]" <<k<< "    "<<j<<   "      "<<DeNumeratorwithoutsmooth<<endl;
            }
            prob_wordsGivenCatsNP2[i][j] = (1 + Numeratorwithoutsmooth) / (v2.size() + DeNumeratorwithoutsmooth);
        }
    }

    param_.num_categories = num_categories;
    param_.priors_cat = prob_cat;
    param_.prob_wordsGivenCatsNP1 = prob_wordsGivenCatsNP1;
    param_.prob_wordsGivenCatsVP = prob_wordsGivenCatsVP;
    param_.prob_wordsGivenCatsNP2 = prob_wordsGivenCatsNP2;
    return param_;
}

void NaiveBayesClassifier::Load(const string& filename)
{
    ifstream in;
    in.open(filename);
    param_.Unserialize(in);
    in.close();
}

void NaiveBayesClassifier::Save(const string& filename) const
{
    ofstream out;
    out.open(filename);
    param_.Serialize(out);
    out.close();
}

// Convert the story to feature by converting word vectors into wordId vectors.
StoryFeature NaiveBayesClassifier::ConvertStoryToFeature(const StoryInfo& story) const
{    
    StoryFeature feature;
    feature.wordIds_np1 = ConvertWordsToIds(story.words_np1, param_.vocabulary_np1);
    feature.wordIds_vp = ConvertWordsToIds(story.words_vp, param_.vocabulary_vp);
    feature.wordIds_np2 = ConvertWordsToIds(story.words_np2, param_.vocabulary_np2);
    return feature;
}


// Convert the word vector to wordId vector by looking up vocabulary.
vector<int> NaiveBayesClassifier::ConvertWordsToIds(
    const vector<string>& words,
    const vector<string>& vocabulary) const
{
    vector<int> wordIds(words.size());
    for (int i = 0; i < words.size(); i++)
    {
        string word = words[i];        
        wordIds[i] = FindWordId(vocabulary, word);
    }
    return wordIds;
}

int NaiveBayesClassifier::FindWordId(const vector<string>& vocabulary, const string& word) const
{
    auto found = find(vocabulary.begin(), vocabulary.end(), word);        
    if (found == vocabulary.end())
    {
        return -1;
    }
    else
    {
        return int(found - vocabulary.begin());
    }
}

vector<double> NaiveBayesClassifier::CalcualtePostProbCats(
    const vector<int>& wordIds,
    const Matrix& prob_wordsGivenCats) const
{
    vector<double> distributionCatGivenWords(param_.num_categories);
    for(int i=0; i < param_.num_categories; i++)
    {
        double prob_wordGivenCat =1;
        for(int j=0; j < wordIds.size(); j++)
        {
            int word_id = wordIds[j];
            if (word_id == -1)
            {
                continue;   // skip the word if not in the vocabulary
            }
            prob_wordGivenCat *= prob_wordsGivenCats[word_id][i];
        }
        distributionCatGivenWords[i] = prob_wordGivenCat * param_.priors_cat[i];
    }
    distributionCatGivenWords = utility::Normalize(distributionCatGivenWords);
    return distributionCatGivenWords;
}