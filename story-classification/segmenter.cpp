#include "segmenter.h"

#include <math.h>
#include <iostream>

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
}

Segmentation Segmenter::SegmentStories(const vector<Triplet>& triplets)
{
    Segmentation optimal = FindSegmentation(CreateInitialSegmentation(triplets));
    return optimal;
}

Segmentation Segmenter::CreateInitialSegmentation(const vector<Triplet>& triplets)
{
    // TODO: give implementation.
    Segmentation initial;
    return initial;
}

Segmentation Segmenter::FindSegmentation(const Segmentation& initial_segmentation)
{
    Segmentation cur_segmentation = initial_segmentation;
    CalculateScore(cur_segmentation);

    Segmentation next_segmentation = PickCandidate(ProposeCandidates(cur_segmentation));
    
    // Iterative until reach optimum. (local) 
    while (!IsCurrentOptimal(cur_segmentation, next_segmentation))
    {
        cur_segmentation = next_segmentation;
        next_segmentation = PickCandidate(ProposeCandidates(cur_segmentation));
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
            candidates[j].segs.push_back(segmentations[j]);
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
            candidates[j].segs.push_back(segmentations[j+1]);
        }
        CalculateScore(candidates[i]);
    }
    return candidates;
}

// Pick the candidate with the highest score.
Segmentation Segmenter::PickCandidate(const vector<Segmentation>& candidates)
{    
    double max_score = -100000;
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
        // FIXME: add length priors
        // score += log(length_distrib_[segmentation[i].GetNumSentences()]);
        if (i >= 1)
        {
            int prev_category_id = segmentation[i-1].GetPrediction().label_id;
            int cur_category_id = segmentation[i].GetPrediction().label_id;
            score += log(transitionMatrix_[cur_category_id][prev_category_id]);
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