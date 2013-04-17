#include "segmenter.h"

void Segmenter::Train(const vector<StoryInfo> labeled_stories, int num_categories)
{
    classifier_.Train(labeled_stories, num_categories);
    transitionMatrix_ = TrainTransitionMatrix(labeled_stories);
}

Segmentation Segmenter::FindSegmentation(const Segmentation& initial_segmentation)
{
    Segmentation cur_segmentation = initial_segmentation;
    Segmentation next_segmentation = PickCandidate(ProposeCandidates(initial_segmentation));
    
    // Iterative until reach optimum. (local) 
    while (!isCurrentOptimal(cur_segmentation, next_segmentation))
    {
        cur_segmentation = next_segmentation;
        next_segmentation = PickCandidate(ProposeCandidates(initial_segmentation));
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

        // copy others.
        for (int j = i+1; j < segmentations.size() -1; j++)
        {
            candidates[j].segs.push_back(segmentations[j+1]);
        }
    }
}

// Pick the candidate with the highest score.
Segmentation Segmenter::PickCandidate(const vector<Segmentation>& candidates)
{    
    double max_score = -10000;
    int candidate_index = 0;
    for (int i = 0; i < candidates.size(); i++)
    {
        if (candidates[i].score > max_score)
        {
            max_score = candidates[i].score;
            candidate_index = i;
        }
    }
    return candidates[candidate_index];
}

// Calculate score by energy function.
double Segmenter::GetScore(const Segmentation& segmentation)
{   
    // TODO 
    return 0;
}

// Greedy: 
bool Segmenter::isCurrentOptimal(const Segmentation& current, const Segmentation& candidate)
{
    return current.score > candidate.score;
}

Matrix Segmenter::TrainTransitionMatrix(const vector<StoryInfo> stories)
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

    return Normalize2D(transitionMat);
}