//  common.h
//  audio
//
//  Created by Xiao Yang on 16/4/15.
//  Copyright (c) 2016年 Young. All rights reserved.
//

#ifndef audio_common_h
#define audio_common_h

#include <vector>

typedef char   size8_t;
typedef short  size16_t;
typedef int    size32_t;
typedef unsigned int uint;

// set values for flags
template <typename T>
void set_flag_vals(T* flag, std::string vals);

template <typename T>
void pack(T* content, std::vector<float>& samples, uint sample_num, uint start);

template <typename T>
const float avg_pack(T* content, uint sample_num, uint start);

template <typename T>
void intercpy(T* src, T* dst, const uint samp_size, const uint interval);

#endif
