AUDIO
=================

###Intro

Audio is a C++ library  to provide easy access on WAV files. It now provides abilities described as below: 

- Gets header information;
- Downsampling;
- Slicing wav into segments in a specified length, (while no voice were to be truncated);
- Converts stereo to mono;


###Usage

*declare*
```c_cpp
\#include "audio.h"
BaseWave wav;
```

*open*
```c_pp
try{
    wav.open(filename)
}catch(const UnreadableException& e){
    cerr << e.what() << endl;    
    exit(2);
}
```

*write*
```c_pp
wav.normalize();	// to clean header
wav.set_filename("audio.wav");
wav.write();	// or wav.write("audio.wav");
```

###Note

In fact, waveform audio file format is quite flexible and unstrunctured (well, in some sense). Extra bytes and information may be contained in the header, which makes it pretty difficult to parse all info. To simplify processing, all extra bytes were **ignored** and the minimum subset of data were collected. Therefore, after processing, ```normalize()``` was ought to be called to generate a clean, suitable header.

Even though it works for most cases, to be honest, the processing is quite rough. Therefore, the class is not recommended to use for people who wishes to keep other infomation. The alternative way is inheriting the base class and implementing your own ```open``` and ```write``` methods.

A documentation - [*Multimedia Programming Interface and Data Specifications 1.pdf*](http://www.tactilemedia.com/info/MCI_Control_Info.html) describing all specification is contained in current directory, *page 65~76* focuses on waveform audio file format.

###TODO

The library is about to provide more common functions in the future:

1. *voice segment*: split wav into snippets to make each of which contains an unbroken semantic voice;
1. *extract*: extracts a segment with given begining and ending.

Happy Writing!