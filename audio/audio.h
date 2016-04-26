//
//  audio.h
//  
//
//  Created by Xiao Yang on 16/4/8.
//
//

#ifndef ____audio__
#define ____audio__
#define _CRT_SECURE_NO_WARNINGS

#include <fstream>
#include "common.h"

#define HEADER_SIZE_DEF 44

typedef struct {
    size8_t   riff_flag[4]; // "RIFF"
    size32_t  size;         // size of overall file, equals to data_size + 44
    size8_t   wave_flag[4]; // "WAVE"
    size8_t   fmt_flag[4];  // "fmt\0"
    size32_t  length;       // length of format data as listed above, always 16
    size16_t  tag;          // type of format, 1 stands for PCM
    size16_t  channels;     // number of channels
    size32_t  sample_rate;  // sample rate = number of samples per second, or Hertz
    size32_t  byte_rate;    // SampleRate * BitsPerSample * Channels / 8, number of bytes per second
    size16_t  sample_bytes; // BitsPerSamle * channels / 8, bytes per sample
    size16_t  sample_width; // bits per sample
    size8_t   data_flag[4]; // "data"
    size32_t  data_size;    // size of data section
    
}wave_header_t;  // header lenght 44 bytes

typedef union {
    wave_header_t   header;
    char            buffer[HEADER_SIZE_DEF];
}header_buffer_t;


class BaseWave {
   
protected:
    wave_header_t   wave_header;// 44 bytes' header information
    const char*     content;    // pointer to content
    const char*     filename = nullptr;
    
    header_buffer_t header_buffer;  // to read and save
    fstream         fs;         // file pointer if exists
    const uint SUFFIX_LENGTH = 4;   // .wav
    const char INDEX_SEP = '_';
    
public:
    BaseWave(){};
    BaseWave(const BaseWave& other);
    ~BaseWave(){
        delete [] content;
        delete [] filename;
        fs.close();
    };
    
    static const unsigned short HEADER_SIZE = HEADER_SIZE_DEF;
    static const char* RIFF;
    static const char* WAVE;
    static const char* FMT;
    static const char* DATA;
    
    // append "\0" at the end of the flag so that it could be printed correctly
    static const char* flag_to_str(const size8_t* flag, uint length)  {
        char * cstr = new char [length + 1];
        strcpy(cstr, (char*)(flag));
        cstr[length] = '\0';
        return cstr;
    }
    
    friend ostream& operator<<(ostream& out, const BaseWave& w){
        const char* riff_flag_str = flag_to_str(w.wave_header.riff_flag, 4);
        const char* wave_flag_str = flag_to_str(w.wave_header.wave_flag, 4);
        const char* fmt_flag_str  = flag_to_str(w.wave_header.fmt_flag, 4);
        const char* data_flag_str = flag_to_str(w.wave_header.data_flag, 4);
        
        out << "HEADER INFO:\nriff flag: " << riff_flag_str << "\nfile size: " << w.wave_header.size;
        out << "\nwave flag: " << wave_flag_str << "\nfmt flag: " << fmt_flag_str;
        out << "\nfmt length: " << w.wave_header.length << "\ntag: " << w.wave_header.tag;
        out << "\nchannels: " << w.wave_header.channels << "\nsample rate: " << w.wave_header.sample_rate;
        out << "\nbyte rate: " << w.wave_header.byte_rate << "\nbytes per frame: " << w.wave_header.sample_bytes;
        out << "\nbits per sample: " << w.wave_header.sample_width << "\ndata flag: " << data_flag_str;
        out << "\ndata size: " << w.wave_header.data_size << endl;
        
        delete [] riff_flag_str;
        delete [] wave_flag_str;
        delete [] fmt_flag_str;
        delete [] data_flag_str;
        return out;
    }
    
    void set_sample_rate(const uint sample_rate);
    void set_data_size(const uint data_size);
    void set_content_ptr(const char* ptr);
    
    void open(const char* filename);    // open a wav file
    void write();
    void write(const char* filename);
    bool is_valid(wave_header_t header) const;  // to check if all flags are set correctly
    void set_header(const BaseWave& wav);   // copy wav.wave_header to this
    void set_header(const uint channels, const uint sample_rate, const uint sample_width);
    void set_filename(const char* new_name);
    
    const uint time2bytes(const float duration) const;    // gets the number of bytes used in the duration
    const uint time2samples(const float duration) const;    // gets the number of samples need in the duration
    const uint get_samples_num() const;
    const float get_duraion() const;
    const float get_samples_avg(const uint begining_byte, const uint bytes_num) const;  // get the avarage value of samples from the begining byte with the size of bytes_num
    
    void lower_sampling(const uint low_samp_rate=8000);     // lowring samples according to the new low_sample_rate
    const char* get_clip_name(uint index);      // return "$filename_1.wav"
    vector<BaseWave*>& truncate(const uint max_duration, vector<BaseWave*>& wav_vec);         // split wav into pieces if its duration was over the max_duration
    vector<BaseWave*>& smart_truncate(const uint max_duraion, vector<BaseWave*>& wav_vec, float window=0.5, float threshold=200.0, const float offset=0.1);   // truncate but make sure no voice were splited
    BaseWave* wave_clip(const uint clip_begining_byte, const uint clip_size, const char* clip_name);
    
    // to catch error caused by platform changed
    void test_type_size();
    void test_avg_pack();
};


#endif /* defined(____audio__) */
