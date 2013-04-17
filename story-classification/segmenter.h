#ifndef _SEGMENTER_H_
#define _SEGMENTER_H_ value

#include <vector>

#include "classifier.h"
#include "definitions.h"
#include "utility.h"

using namespace utility;

class Segment
{
public:    
    void Merge(const Segment& other)
    {
        // TODO: Give Implementation.
    }
protected:
// TODO: segment representation
};

class Segmentation
{
public:
    vector<Segment> segs;
    double score;
    Segment operator[](int i) const {return segs[i];}

    int size() const {return segs.size();}
};


class Segmenter
{
public:
    // Train
    void Train(const vector<StoryInfo> labeled_stories, int num_categories);

    // Deploy    
    Segmentation FindSegmentation(const Segmentation& initial_segmentation);

private:
    // Train
    Matrix TrainTransitionMatrix(const vector<StoryInfo> stories);

    // Greedy strategy
    vector<Segmentation> ProposeCandidates(const Segmentation& segmentations);
    Segmentation PickCandidate(const vector<Segmentation>& candidates);
    bool isCurrentOptimal(const Segmentation& current, const Segmentation& candidate);
    double GetScore(const Segmentation& segmentation);

private:
    NaiveBayesClassifier classifier_;
    Matrix transitionMatrix_;
};

#endif