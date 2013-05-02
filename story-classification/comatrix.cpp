#include "comatrix.h"

#include <iostream>
#include <unordered_map>
#include <string>
#include "utility.h"
#include <fstream>
#include <algorithm>
#include <stdio.h>

using namespace std;

void CooccurrenceMatrix::BuildMatrix(const vector<Sentence>& sentences)
{
    // Build vocabulary
    unordered_map<string, int> vocabulary_np1;
    unordered_map<string, int> vocabulary_vp;
    unordered_map<string, int> vocabulary_np2;

    vector<string> voc_np1;
    vector<string> voc_vp;
    vector<string> voc_np2;

    int np1_count = 0;
    int vp_count = 0;
    int np2_count = 0;
    for_each(sentences.begin(), sentences.end(), [&] (Sentence sen){
        // Build np1 vocabulary
        for_each(sen.words_np1.begin(), sen.words_np1.end(), [&] (string np1) {
            if (vocabulary_np1.find(np1) == vocabulary_np1.end()){
                vocabulary_np1[np1] = np1_count;
                voc_np1.push_back(np1);
                np1_count++;
            }
        });

        // Build vp vocabulary
        for_each(sen.words_vp.begin(), sen.words_vp.end(), [&] (string vp) {
            if (vocabulary_vp.find(vp) == vocabulary_vp.end()){
                vocabulary_vp[vp] = vp_count;
                voc_vp.push_back(vp);
                vp_count++;
            }
        });

        // Build np2 vocabulary
        for_each(sen.words_np2.begin(), sen.words_np2.end(), [&] (string np2) {
            if (vocabulary_np2.find(np2) == vocabulary_np2.end()){
                vocabulary_np2[np2] = np2_count;
                voc_np2.push_back(np2);
                np2_count++;
            }
        });
    });

    printf("# of NP1:\t%d\n", np1_count);
    printf("# of VP:\t%d\n", vp_count);
    printf("# of NP2:\t%d\n", np2_count);

    // Build matrix: 2D NP1 VP
    utility::Matrix mat = utility::BuildMatrix(np1_count, vp_count);
    for_each(sentences.begin(), sentences.end(), [&] (Sentence sen){
        for_each(sen.words_np1.begin(), sen.words_np1.end(), [&] (string np1) {
            for_each(sen.words_vp.begin(), sen.words_vp.end(), [&] (string vp) {
                mat[vocabulary_np1[np1]][vocabulary_vp[vp]] += 1;
            });
        });
    });

    ofstream out;
    out.open("output/co_mat.txt");
    out << "Total Times:\t" << 1 << endl;
    out << "Total Samples:\t" << vp_count << endl;
    out << "Total Genes:\t" << np1_count << endl;
    out << "Time\t" << 0 << endl;
    out << "ID" << '\t' << "NP1";
    for (int i = 0; i < voc_vp.size(); i++)
    {
        out << '\t' << voc_vp[i];
    }
    out << endl;

    for (int i = 0; i < mat.size(); i++)
    {
        out << i << '\t' << voc_np1[i];
        for (int j = 0; j < mat[i].size(); j++)
        {
            out << '\t' << mat[i][j];
        }
        out << endl;
    }
    out.close();
}