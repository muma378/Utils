//
//  main.cpp
//  audio
//
//  Created by Xiao Yang on 16/4/8.
//  Copyright (c) 2016年 Young. All rights reserved.
//


#include "audio.h"


int main(int argc, const char * argv[]) {
//    BaseWave wav = BaseWave(1, 16000, 16, 0);
    BaseWave wav;
    wav.open("/Users/imac/Desktop/test.wav");
    wav.test_avg_pack();
    wav.lower_sampling(8000);
    vector<BaseWave*> wav_vec;
    wav.smart_truncate(3*60, wav_vec);
    for (vector<BaseWave*>::iterator it=wav_vec.begin(); it != wav_vec.end(); it++) {
        (*it)->write();
    }
//    wav.write("/Users/imac/Desktop/low_test1.wav");

    
    return 0;
}
