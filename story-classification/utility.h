#ifndef _UTILITY_H_
#define _UTILITY_H_

#include <vector>
#include <string>
#include <iostream>

using namespace std;

namespace utility
{

    typedef vector< vector<double> > Matrix;

    Matrix BuildMatrix(int num_rows, int num_columns, double default_value = 0);

    vector<double> Normalize(const vector<double>& countVector);

    // Matrix A[i][j] each column normalized to 1,
    // so that  \sum_{i} A[i][j] = 1  for any j.
    Matrix Normalize2D(const Matrix& countMatrix, bool column_wise = true);

    std::string trim_front(const std::string& str, const std::string& trimChars);
}


template <class T>
ostream& operator << (ostream& os, const vector<T>& v)
{
    os << v.size() << endl;
    for (int i = 0; i < v.size(); i++)
    {
        os << v[i] << endl;
    }
    return os;
}

template <class T>
istream& operator >> (istream& is, vector<T>& v)
{
    int size = 0;
    is >> size;
    v.resize(size);

    for (int i = 0; i < v.size(); i++)
    {
        is >> v[i];
    }
    return is;
}

#endif
