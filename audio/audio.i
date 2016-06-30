%module audio
%{
#define SWIG_FILE_WITH_INIT
#include <iostream>
#include <string>
#include "common.h"
#include "audio.h"
#include "exceptions.h"
%}

%include "exceptions.h"

%include "common.h"
%template(set_flag_chars) set_flag_vals<char>;
%template(pack_size8_t) pack<size8_t>;
%template(pack_size16_t) pack<size16_t>;
%template(pack_size32_t) pack<size32_t>;
%template(avg_pack_size8_t) avg_pack<size8_t>;
%template(avg_pack_size16_t) avg_pack<size16_t>;
%template(avg_pack_size32_t) avg_pack<size32_t>;
%template(intercpy_size8_t) intercpy<size8_t>;
%template(intercpy_size16_t) intercpy<size16_t>;
%template(intercpy_size32_t) intercpy<size32_t>;

%include "std_vector.i"
namespace std {
        %template(FloatVec) vector<float>;
        %template(BaseWaveVec) vector<BaseWave *>;
};

%include "audio.h"
%rename(__eq__) BaseWave::operator=;
%ignore BaseWave::operator<<;
%extend BaseWave{
        char* __str__() {
                std::cout << *$self;
                char end = '\0';
                return &end;
        }
};

%include "exception.i"
