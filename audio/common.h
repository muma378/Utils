//  common.h
//  audio
//
//  Created by Xiao Yang on 16/4/15.
//  Copyright (c) 2016年 Young. All rights reserved.
//

#ifndef audio_common_h
#define audio_common_h

#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <assert.h>

#include "exceptions.h"

using namespace std;

typedef char   size8_t;
typedef short  size16_t;
typedef int    size32_t;
typedef unsigned int    uint;

// set values for flags
template <typename T>
void set_flag_vals(T* flag, string vals) {
    for (int i=0; i<vals.length() ; i++) {
        flag[i] = vals.at(i);
    }
    return;
};


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



#endif
