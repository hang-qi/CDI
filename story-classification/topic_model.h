#include "definitions.h"
#include "utility.h"

#include <vector>
#include <memory>
#include <iostream>

using namespace std;

class Node;

//
// Topic hierarchy is a And-Or Tree.
//
class TopicHierarchy
{
public:
    void FeedStories(const vector<StoryInfo>& stories);
    void FeedStory(const StoryInfo& story);

    // Print out the topic hierarchy.
    void PrintHierarchy(ostream& os);

    // save and load the model from file.
    void Save(const string& filename);
    void Load(const string& filename);
private:
    unique_ptr<Node> root_;
};

//
// Node class.
//
class Node
{
public:

private:
    vector< unique_ptr<Node> > children_;
};

//
// TopicNodes are terminal nodes in the topic hierarchy. 
//
class TopicNode : Node
{
public:
    double GetLikelihood(StoryInfo story);

    // Synthesize a title for this topic.
    string SynthesizeTitle();

protected:
    Node* Split()
    {
        return nullptr;
    }

private:    
    vector<StoryInfo> stories_;

    vector<string> vocabulary_np1_;
    vector<string> vocabulary_vp_;
    vector<string> vocabulary_np2_;

    vector<double> distribution_np1_;
    vector<double> distribution_vp_;
    vector<double> distribution_np2_;

    utility::Matrix data_matrix_;
    utility::Matrix co_occurrence_matrix;
};