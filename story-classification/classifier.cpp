#include "classifier.h"

namespace stat_utility
{
    vector<double> Normalize(const vector<double>& countVector)
    {
        int num_elements = countVector.size();
        vector<double> prob(num_elements, 0);
        
        double sum = 0;
        for (int i=0; i< num_elements; i++)
        {
            sum += countVector[i];
        }

        if (sum != 0)
        {
            for (int i=0; i < num_elements; i++)
            {        
                prob[i] = countVector[i]/sum;
            }
        }
        return std::move(prob);
    }
}

// Convert the word vector to wordId vector by looking up vocabulary.
vector<int> NaiveBayesClassifier::ConvertWordsToIds(
    const vector<string>& words,
    const vector<string>& vocabulary)
{
    vector<int> wordIds(words.size());
    for (int i = 0; i < words.size(); i++)
    {
        wordIds[i] = FindWordId(vocabulary, words[i]);
    }
    return wordIds;
}

// Convert the story to feature by converting word vectors into wordId vectors.
StoryFeature NaiveBayesClassifier::ConvertStoryToFeature(const StoryInfo& story)
{    
    StoryFeature feature;
    feature.wordIds_np1 = ConvertWordsToIds(story.words_np1, param_.vocabulary_np1);
    feature.wordIds_vp = ConvertWordsToIds(story.words_vp, param_.vocabulary_vp);
    feature.wordIds_np2 = ConvertWordsToIds(story.words_np2, param_.vocabulary_np2);
    return feature;
}

vector<double> NaiveBayesClassifier::CalcualtePostProbCats(
    const vector<int>& wordIds,
    const Matrix& prob_wordsGivenCats)
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
    distributionCatGivenWords = stat_utility::Normalize(distributionCatGivenWords);
    return distributionCatGivenWords;
}

int NaiveBayesClassifier::Predict(const StoryInfo& story)
{
    StoryFeature storyfeature = ConvertStoryToFeature(story);

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

    // Predict by the maximum posterior probability (Bayes Decision).
    // Normalize is not necessary.
    int predicted_category_idx = max_element(dist_catGivenStory.begin(), dist_catGivenStory.end()) - dist_catGivenStory.begin();
    return predicted_category_idx;
}