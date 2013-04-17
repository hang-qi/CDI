#include "utility.h"

namespace utility
{
    Matrix BuildMatrix(int num_rows, int num_columns, double default_value)
    {
        vector<double> vec(num_columns, default_value);
        Matrix mat(num_rows, vec);
        return std::move(mat);
    }

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

    Matrix Normalize2D(const Matrix& countMatrix, bool column_wise)
    {
        int num_rows = countMatrix.size();
        int num_columns = countMatrix[0].size();
        Matrix prob = BuildMatrix(num_rows, num_columns);

        if (column_wise)
        {
            for (int i=0; i< num_columns; i++ )
            {
                double sum_column = 0;
                for (int j=0; j< num_rows; j++)
                {
                    sum_column += countMatrix[j][i];
                }

                for (int j=0; j< num_rows; j++)
                {
                    if (countMatrix[j][i] != 0 && sum_column != 0 )
                    {
                          prob[j][i] = countMatrix[j][i]/sum_column;
                    }
                }
            }
            return std::move(prob);
        }
    }

    std::string trim_front(const std::string& str, const std::string& trimChars)
    {
        int i = 0;
        for (i = 0; i < str.size(); i++)
        {
            bool found = false;
            for (int j = 0; j < trimChars.size(); j++)
            {
                if (str[i] == trimChars[j])
                    found = true;
            }
            if (found == false)
                break;
        }
        return str.substr(i);
    }
}
