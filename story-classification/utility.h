#ifndef _UTILITY_H_
#define _UTILITY_H_

#include <vector>
#include <string>

namespace utility
{
    using namespace std;

    typedef vector< vector<double> > Matrix;

    Matrix BuildMatrix(int num_rows, int num_columns, double default_value = 0);

    vector<double> Normalize(const vector<double>& countVector);

    Matrix Normalize2D(const Matrix& countMatrix, bool column_wise = true);

    std::string trim_front(const std::string& str, const std::string& trimChars);
}

#endif
