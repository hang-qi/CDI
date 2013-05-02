#ifndef _COMATRIX_H_
#define _COMATRIX_H_

#include "definitions.h"
#include <vector>

class CooccurrenceMatrix
{
public:
    void BuildMatrix(const std::vector<Sentence>& sentences);
};

#endif