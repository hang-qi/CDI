#include "segmenter.h"

#include <math.h>
#include <iostream>

#define LEN_INIT_SEGMENT 2

void Segmenter::Load(const string& filename)
{
    ifstream in;
    in.open(filename);
    NBClassifierParameter param;
    param.Unserialize(in);
    classifier_ = NaiveBayesClassifier(param);    
    in >> transitionMatrix_;
    in >> length_distrib_;
    in.close();
}

void Segmenter::Save(const string& filename) const
{
    ofstream out;
    out.open(filename);
    classifier_.GetParameters()->Serialize(out);
    out << transitionMatrix_;
    out << length_distrib_;
    out.close();
}


void Segmenter::Train(const vector<StoryInfo>& labeled_stories, int num_categories)
{
    classifier_.Train(labeled_stories, num_categories);
    transitionMatrix_ = TrainTransitionMatrix(labeled_stories);
    // FIXME: add length priors
    //length_distrib_ = TrainLengthDistribution(labeled_stories);
    TrainLengthDistribution(labeled_stories);
}

void Segmenter::CalculateTrueScore(const vector<Sentence>& sentences,
    const vector<int>& true_segmentation)
{
    Segmentation groundTruth;
    int base = 0;
    for (int i = 0; i < true_segmentation.size(); i++)
    {
        vector<string> words_np1;
        vector<string> words_vp;
        vector<string> words_np2;

        for (int j = 0; j < true_segmentation[i]; j++)
        {
            words_np1.insert(words_np1.end(),
                sentences[base+j].words_np1.begin(), sentences[base+j].words_np1.end());
            words_vp.insert(words_vp.end(),
                sentences[base+j].words_vp.begin(), sentences[base+j].words_vp.end());
            words_np2.insert(words_np2.end(), 
                sentences[base+j].words_np2.begin(), sentences[base+j].words_np2.end());
        }
        base += true_segmentation[i];

        StoryInfo story;
        story.words_np1 = words_np1;
        story.words_vp = words_vp;
        story.words_np2 = words_np2;

        Segment segment(true_segmentation[i], classifier_.ConvertStoryToFeature(story));
        segment.SetPrediction(
            classifier_.Predict(segment.GetStoryFeature()));
        groundTruth.segs.push_back(segment);
    }    
    groundTruth.SetScore(CalculateScore(groundTruth));
    cout << "GROUND-TRUTH SCORE: " << groundTruth.GetScore() << endl;
}

Segmentation Segmenter::DoSegment(const vector<Sentence>& sentences)
{
    Segmentation optimal = FindSegmentation(CreateInitialSegmentation(sentences));
    
    cout << "OPTIMAL SCORE: " << optimal.GetScore() << endl;
    cout << "OPTIMAL SEGMENTATION" << endl;
    for (int i = 0; i < optimal.segs.size(); i++)
    {
        cout << " " << optimal.segs[i].GetNumSentences();
    }
    cout << endl;

    cout << "CATEGORY:" << endl;
    for (int i = 0; i < optimal.segs.size(); i++)
    {
        cout << " " << optimal.segs[i].GetPrediction().label_id;
    }
    cout << endl;
    return optimal;
}

Segmentation Segmenter::CreateInitialSegmentation(const vector<Sentence>& sentences)
{
    // TODO: give implementation.    
    Segmentation initial;

    int base = 0;
    for (int i = 0; i < sentences.size() / LEN_INIT_SEGMENT; i++)
    {
        vector<string> words_np1;
        vector<string> words_vp;
        vector<string> words_np2;

        int seg_size = LEN_INIT_SEGMENT;
        if (i == (sentences.size() / LEN_INIT_SEGMENT) -1)
        {
            seg_size = LEN_INIT_SEGMENT + (sentences.size() % LEN_INIT_SEGMENT);
        }
        for (int j = 0; j < seg_size; j++)
        {
            words_np1.insert(words_np1.end(),
                sentences[base+j].words_np1.begin(), sentences[base+j].words_np1.end());
            words_vp.insert(words_vp.end(),
                sentences[base+j].words_vp.begin(), sentences[base+j].words_vp.end());
            words_np2.insert(words_np2.end(), 
                sentences[base+j].words_np2.begin(), sentences[base+j].words_np2.end());
        }
        base += seg_size;

        StoryInfo story;
        story.words_np1 = words_np1;
        story.words_vp = words_vp;
        story.words_np2 = words_np2;

        Segment segment(seg_size, classifier_.ConvertStoryToFeature(story));
        segment.SetPrediction(
            classifier_.Predict(segment.GetStoryFeature()));
        initial.segs.push_back(segment);
    }
    return initial;
}

Segmentation Segmenter::FindSegmentation(const Segmentation& initial_segmentation)
{
    Segmentation cur_segmentation = initial_segmentation;
    cur_segmentation.SetScore(CalculateScore(cur_segmentation));

    Segmentation next_segmentation = PickCandidate(ProposeCandidates(cur_segmentation));
    
    // Iterative until reach optimum. (local) 
    while (!IsCurrentOptimal(cur_segmentation, next_segmentation)
        && cur_segmentation.size() > 2)
    {
        cur_segmentation = next_segmentation;
        next_segmentation = PickCandidate(ProposeCandidates(cur_segmentation));

        /* Print current result.        
        cout << "CURRENT" << endl;
        for (int i = 0; i < cur_segmentation.segs.size(); i++)
        {
            cout << " " << cur_segmentation.segs[i].GetNumSentences();
        }
        cout << endl;*/
        //cout << "CURRENT SCORE: " << cur_segmentation.GetScore() << endl;
    }
    return cur_segmentation;
}

// Propose candidates for next step by merging /splitting adjacent segments.
vector<Segmentation> Segmenter::ProposeCandidates(const Segmentation& segmentations)
{
    // Merge adjacent ones. So that n segments will yield n-1 new candidates,
    // and each of the new candidates will have n-1 segments.
    vector<Segmentation> candidates(segmentations.size() -1);
    for (int i = 0; i < candidates.size(); i++)
    {
        // copy previous.
        for (int j = 0; j < i; j++)
        {
            candidates[i].segs.push_back(segmentations[j]);
        }

        // merge the i-th element.
        Segment newSegment = segmentations[i];        
        newSegment.Merge(segmentations[i+1]);
        newSegment.SetPrediction(
            classifier_.Predict(newSegment.GetStoryFeature()));
        candidates[i].segs.push_back(newSegment);

        // copy others.
        for (int j = i+1; j < segmentations.size() -1; j++)
        {
            candidates[i].segs.push_back(segmentations[j+1]);
        }
        candidates[i].SetScore(CalculateScore(candidates[i]));
    }
    return candidates;
}

// Pick the candidate with the highest score.
Segmentation Segmenter::PickCandidate(const vector<Segmentation>& candidates)
{
    double max_score = candidates[0].GetScore();
    int candidate_index = 0;
    for (int i = 0; i < candidates.size(); i++)
    {        
        if (candidates[i].GetScore() > max_score)
        {
            max_score = candidates[i].GetScore();
            candidate_index = i;
        }
    }
    return candidates[candidate_index];
}

// Measure score by -energy.
double Segmenter::CalculateScore(Segmentation& segmentation)
{   
    double score = 0;
    for (int i = 0; i < segmentation.size(); i++)
    {
        score += log(segmentation[i].GetPrediction().joint_prob);

        /*if (segmentation[i].GetNumSentences() == LEN_INIT_SEGMENT)
        {
            score += log(0.1);
        }*/

        // FIXME: add length priors
        // score += log(length_distrib_[segmentation[i].GetNumSentences()]);
        
        if (i >= 1)
        {
            int prev_category_id = segmentation[i-1].GetPrediction().label_id;
            int cur_category_id = segmentation[i].GetPrediction().label_id;
            score += log(transitionMatrix_[cur_category_id][prev_category_id] + 1e-100);
        }
    }
    return score;
}

// Greedy.
bool Segmenter::IsCurrentOptimal(const Segmentation& current, const Segmentation& candidate)
{
    return current.GetScore() > candidate.GetScore();
}

vector<double> Segmenter::TrainLengthDistribution(const vector<StoryInfo>& stories)
{
    // TODO
    /*
    ofstream out;
    out.open("output/length.txt");
    std::for_each(stories.begin(), stories.end(), [&] (StoryInfo story) {
        out << story.num_sentences << endl;
    });
    out.close();*/
    return vector<double>();
}

Matrix Segmenter::TrainTransitionMatrix(const vector<StoryInfo>& stories)
{
    Matrix transitionMat = BuildMatrix(
        classifier_.GetParameters()->num_categories,
        classifier_.GetParameters()->num_categories);

    int prev_category_id = -1;
    int prev_doc_id = -1;
    for (int i = 0; i< stories.size(); i++)
    {
        int cur_doc_id = stories[i].document_id;
        int cur_category_id = stories[i].category_id;

        // Only count transitions within one document / one program
        if (cur_doc_id == prev_doc_id)
        {
            transitionMat[cur_category_id][prev_category_id] += 1;
        }

        prev_category_id = cur_category_id;
        prev_doc_id = cur_doc_id;
    }

    return std::move(Normalize2D(transitionMat));
}