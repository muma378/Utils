//
//  audio.cpp
//  
//
//  Created by Xiao Yang on 16/4/8.
//
//

#include "audio.h"

const char* BaseWave::RIFF = "RIFF";
const char* BaseWave::WAVE = "WAVE";
const char* BaseWave::FMT  = "fmt ";
const char* BaseWave::DATA = "data";


inline void BaseWave::set_sample_rate(const uint sample_rate){
    wave_header.sample_rate = sample_rate;
    wave_header.byte_rate = sample_rate * wave_header.sample_width * wave_header.channels / 8;
    return;
};

inline void BaseWave::set_data_size(const uint data_size){
    wave_header.data_size = data_size;
    wave_header.size = data_size + 44;
    return;
};

inline void BaseWave::set_content_ptr(const char *ptr){
    content = ptr;
}

BaseWave::BaseWave(const BaseWave& other): wave_header(other.wave_header), content(other.content){
}

void BaseWave::set_filename(const char *new_name){
    uint name_len = (unsigned)strlen(new_name);
    if (filename) { // not a null ptr
        delete [] filename;
    }
    char* temp_name = new char[name_len+1];
    for (uint i=0; i<name_len; i++) {
        temp_name[i] = new_name[i];
    }
    temp_name[name_len] = '\0';
    filename = temp_name;
}


void BaseWave::set_header(const uint channels, const uint sample_rate, const uint sample_width){
    // set flags
    set_flag_vals(wave_header.riff_flag, RIFF);
    set_flag_vals(wave_header.wave_flag, WAVE);
    set_flag_vals(wave_header.fmt_flag, FMT);
    set_flag_vals(wave_header.data_flag, DATA);
    
    // set parameters
    wave_header.length      = 16;
    wave_header.tag         = 1;
    wave_header.channels    = channels;
    wave_header.sample_rate = sample_rate;
    wave_header.sample_width= sample_width;
    wave_header.data_size   = 0;    //
    
    wave_header.size        = wave_header.data_size + 44;
    wave_header.byte_rate   = sample_rate * sample_width * channels / 8;
    wave_header.sample_bytes= sample_width * channels / 8;
    return;
}

void BaseWave::set_header(const BaseWave& other){
    set_header(other.wave_header.channels, other.wave_header.sample_rate, other.wave_header.sample_width);
}

bool BaseWave::is_valid(wave_header_t h) const {
    if (strncmp((const char*)h.riff_flag, RIFF, 4) ||
        strncmp((const char*)h.wave_flag, WAVE, 4) ||
        strncmp((const char*)h.fmt_flag, FMT, 4) ||
        strncmp((const char*)h.data_flag, DATA, 4)) {
        return false;
    }
    return true;	// return ture if all flags above were correct 
}


void BaseWave::open(const char* filename){
    fs.open(filename, fstream::in | fstream::binary);
    fs.read(header_buffer.buffer, FIXED_HEADER_SIZE);       // read header to the union
    seek_dataflag();
    fs.read(header_buffer.buffer+FIXED_HEADER_SIZE, FLOAT_HEADER_SIZE);
    
    if (is_valid(header_buffer.header)){
        wave_header = header_buffer.header;
        delete [] content;
        char* data_ptr = new char[wave_header.data_size];
        fs.read(data_ptr, wave_header.data_size);
        set_content_ptr(data_ptr);
        set_filename(filename);
        // cout << *this << endl;
    }else{
        throw UnreadableException("invalid wave header format");
    }
}

void BaseWave::seek_dataflag(){
    char next_character = fs.peek();
    char* trash = new char;
    while (strncmp(&next_character, DATA, 1)) {
        fs.read(trash, 1);  // thrown to bin
        next_character = fs.peek(); // return the next character but not extracting
    }
    delete trash;
    return;

}


void BaseWave::write(){
    if (filename != nullptr && strlen(filename)) {
        write(filename);
    }else{
        throw UnwritableException("no filename is specified to write");
    }
}

void BaseWave::write(const char* filename){
    ofstream ofs(filename, fstream::out|fstream::binary);
    
    header_buffer.header = wave_header;
    if (ofs.is_open()) {
        ofs.write(header_buffer.buffer, HEADER_SIZE);
        ofs.write(content, wave_header.data_size);
        ofs.close();
    }
    
}

const float BaseWave::get_duraion() const{
    return wave_header.data_size / float(wave_header.byte_rate);
}

const uint BaseWave::get_samples_num() const{
    return uint(wave_header.data_size/wave_header.sample_bytes);
}


const uint BaseWave::time2bytes(const float duration) const{
    return uint(wave_header.byte_rate * duration);
}


const uint BaseWave::time2samples(const float duration) const{
    return uint(wave_header.sample_rate * wave_header.channels * duration);
}

const float BaseWave::get_samples_avg(const uint begining_byte, const uint bytes_num) const{
    switch (wave_header.sample_width) {
        case 8:
            return avg_pack(content, bytes_num, begining_byte);     // samples_num = bytes_num * 8/
        case 16:
            return avg_pack((size16_t*)content, bytes_num/2, begining_byte/2);
        case 32:
            return avg_pack((size16_t*)content, bytes_num/4, begining_byte/4);
            
        default:
            const char* err_msg = ("width of sample detected is not in the range: " + to_string(wave_header.sample_width)).c_str();
            throw UnreadableException(err_msg);
    }
}


void BaseWave::lower_sampling(const uint low_samp_rate){
    uint lower_rate = uint(wave_header.sample_rate / low_samp_rate);
    uint new_data_size = wave_header.data_size/lower_rate;
    char* samples = new char[new_data_size];
    uint sample_loop = wave_header.sample_bytes * lower_rate;
    
    if (lower_rate > 1){
        uint j = 0;
        for (uint i=0; i < wave_header.data_size; i++) {
            if (i%sample_loop < wave_header.sample_bytes) { // only copies N continuous bytes in M bytes while M/N is lower_rate
                samples[j] = content[i];
                j++;
            }
        }
        set_data_size(new_data_size);
        set_sample_rate(low_samp_rate);
        delete [] content;  // delete space allocated
        content = samples;
	}
	else{
		if (lower_rate < 1){
			cout << "sampling rate is " << wave_header.sample_rate << ", which is less than " << low_samp_rate << endl;
		}
	}
    return;
        
}

// return the name of
const char* BaseWave::get_clip_name(uint index){
    string filename_str(filename);
    filename_str.insert(filename_str.length()-SUFFIX_LENGTH, INDEX_SEP+to_string(index));
	unsigned long name_length = filename_str.length() + 1;
	char* clip_name = new char[name_length];
	strcpy(clip_name, filename_str.c_str());
    return clip_name;
}



// split wav into clips if its duration was over the max_duration
vector<BaseWave*>& BaseWave::truncate(const uint max_duration, vector<BaseWave*>& clips_vec){
    clips_vec.clear();
    const uint max_clip_bytes = time2bytes(max_duration);
    if (max_clip_bytes > wave_header.data_size) {
        clips_vec.push_back(this);    // no need to truncate, return its self
    }else{
        uint clip_begining_byte = 0;
        uint clip_ending_byte = 0;
        uint counter = 0;
        while (clip_ending_byte < wave_header.data_size) {      // if the last clip split has not reached the ending of the file
            clip_begining_byte = clip_ending_byte;
            clip_ending_byte = clip_begining_byte + max_clip_bytes;
            if (wave_header.data_size < clip_ending_byte) {
                clip_ending_byte = wave_header.data_size;
            }
            uint  clip_size = clip_ending_byte - clip_begining_byte;
			const char* clip_name = get_clip_name(counter++);
            clips_vec.push_back(wave_clip(clip_begining_byte, clip_size, clip_name));
			delete[] clip_name;
        }
    }
    return clips_vec;
};

// truncate but make sure no voice were splited
vector<BaseWave*>& BaseWave::smart_truncate(const uint max_duraion, vector<BaseWave*>& clips_vec, float window, float threshold, const float offset){
    clips_vec.clear();
    
    const uint max_clip_bytes = time2bytes(max_duraion);
    const uint bytes_in_window = time2bytes(window);
    
    if (max_clip_bytes > wave_header.data_size) {
        clips_vec.push_back(this);    // no need to truncate, return its self
    }else{
        uint clip_ending_byte = 0;
        uint clip_begining_byte = 0;
        uint counter = 0;
        while (clip_ending_byte < wave_header.data_size) {      // if the last clip split has not reached the ending of the file
            clip_begining_byte = clip_ending_byte;
            
            clip_ending_byte = clip_begining_byte + max_clip_bytes;
            if (wave_header.data_size < clip_ending_byte) {
                clip_ending_byte = wave_header.data_size;
            }else{
                // lookin for the ending with no voice inside
                uint ending_offset = 0;
                while (true) {
                    uint window_begining_byte = clip_ending_byte - bytes_in_window - ending_offset;
                    if (window_begining_byte <= clip_begining_byte) {  // failed to find an avaible ending with this threshold
                        threshold = threshold * 2;  // loosen the threshold
                        ending_offset = 0;     // start from begining
                    }
                    if (get_samples_avg(window_begining_byte, bytes_in_window) > threshold) {   // if the average value of the window was under the threshold
                        ending_offset += time2bytes(offset);    // shifting the potential ending
                    }else{
                        clip_ending_byte -= ending_offset;  // the ending was found
                        break;
                    }
                }
            }
            uint  clip_size = clip_ending_byte - clip_begining_byte;
            const char* clip_name = get_clip_name(counter++);
            clips_vec.push_back(wave_clip(clip_begining_byte, clip_size, clip_name));
            delete [] clip_name;
        }
    }
    
    return clips_vec;
}

BaseWave* BaseWave::wave_clip(const uint clip_begining_byte, const uint clip_size, const char* clip_name){
    char* clip_content = new char[clip_size];
    memcpy(clip_content, content+clip_begining_byte, clip_size);    //copy a slice of content to the clip
    
    BaseWave* clip = new BaseWave(*this);
    clip->set_data_size(clip_size);
    clip->set_content_ptr(clip_content);
    clip->set_filename(clip_name);
    return clip;
}

// test if the program goes as we thought
void BaseWave::test_avg_pack(){
	const uint start_byte = int(wave_header.data_size) / 3;
    float samples_avg_1 = get_samples_avg(start_byte, 10);
    vector<float> samples_vec;
    pack((size16_t*)content, samples_vec, 10/2, start_byte / 2);
    float samples_avg_2 = 0;
    for (vector<float>::iterator it=samples_vec.begin();it != samples_vec.end() ; it++) {
        samples_avg_2 += abs(*it);
    }
    assert(samples_avg_1 == samples_avg_2/5);
}

// test if the operation system was as same as our development environment
void BaseWave::test_type_size() {
    if (sizeof(size8_t) == 1 &&
        sizeof(size16_t) == 2 &&
        sizeof(size32_t) == 4){
        return;
    }
    else{
        cerr << "critical error: types' size of the platform in use are not as same as the macros defined\n"
        << "please get the source code, alter it and then rebuild." << endl;
        exit(1);
    }
}

