
#include <vector>
#include <string>
#include "common.h"

using namespace std;

// set values for flags
template <typename T>
void set_flag_vals(T* flag, string vals) {
    for (int i=0; i<vals.length() ; i++) {
        flag[i] = vals.at(i);
    }
    return;
}


template <typename T>
void pack(T* content, vector<float>& samples, uint sample_num, uint start){
    samples.clear();
    for (int i=start; i<sample_num+start; i++) {
        samples.push_back(*(content+i));
    }
    return;
}

template <typename T>
const float avg_pack(T* content, uint sample_num, uint start) {
    float sum = 0;
    for (int i=start; i<sample_num+start; i++) {
        sum += abs(*(content+i));
    }
    return sum/sample_num;
}

template <typename T>
void intercpy(T* src, T* dst, const uint samp_size, const uint interval){
    for (uint i=0, j=0; i<samp_size; i+=interval) {
        dst[j++] = src[i];
    }
    return;
}