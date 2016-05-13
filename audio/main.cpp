//
//  main.cpp
//  audio
//	exit with critical error (for system, operation and etc) return 1, 
//  with error happened in reading returns 2, error occured in writting returns 3
//  Created by Xiao Yang on 16/4/8.
//  Copyright (c) 2016年 Young. All rights reserved.
//


#include "audio.h"
#include "common.h"
#include "exceptions.h"

using namespace std;

int main(int argc, const char * argv[]) {
//    BaseWave wav = BaseWave(1, 16000, 16, 0);
	
	BaseWave wav = BaseWave();
    wav.test_type_size();

	if (argc != 3){
		cout << "number of arguments is incorrect\n";
		cout << "usage: " << argv[0] << " src_file dst_file" << endl;
		return 1;
	}
	const char* src_file = argv[1];
	const char* dst_file = argv[2];
    
	try{
		wav.open(src_file);
        wav.test_avg_pack();
       // cout << wav << endl;
	}
	catch (const UnreadableException& e){	
		cerr << e.what() << endl;;
		exit(2);
	}
  
//    BaseWave mono = wav.stereo2mono();
//    mono.set_filename(dst_file);
//    mono.normalize();
//    mono.write();
    
    if (wav.is_stereo()) {
        BaseWave mono = wav.stereo2mono();
        mono.set_filename(dst_file);
        wav = mono;
    }
    
    if(!wav.is_normalized()){
        wav.normalize();
    }
    
    wav.downsample(8000);
	//wav.write(argv[2]);
	vector<BaseWave*> wav_vec;
	wav.set_filename(dst_file);		// alter the filename to renew the place to save
    wav.smart_slice(30*60, wav_vec);		// cause smart_truncate will generate files in the same directory
	try{
		for (vector<BaseWave*>::iterator it = wav_vec.begin(); it != wav_vec.end(); it++) {
			(*it)->write();
		}
	}
	catch (const UnwritableException& e){
		cerr << e.what() << endl;
		exit(3);
	}
    return 0;
}
