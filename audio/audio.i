%module audio
%{
#define SWIG_FILE_WITH_INIT
#include <iostream>
#include <string>
#include "common.h"
#include "audio.h"
%}


typedef char size8_t;
typedef short   size16_t;
typedef int     size32_t;
typedef unsigned int uint;
void validate_typesize();


%include "std_vector.i"
namespace std {
        %template(BaseWaveVec) vector<BaseWave *>;
}
%include "audio.h"
%extend BaseWave{
        char* __str__() {
                std::cout << *$self;
                char end = '\0';
                return &end;
        }
};

