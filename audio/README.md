AUDIO
=================

**Intro**

Audio is a C++ library  to provide easy access on WAV files. It now provides abilities described as below: 

- Gets header information;
- Downsampling;
- Slicing wav into segments in a specified length, (while no voice were to be truncated);
- ...


**Usage**

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

**TODO**

The library is about to provide more common functions in the future:

1. *voice segment*: split wav into snippets to make each of which contains an unbroken semantic voice;
1. *extract*: extracts a segment with given begining and ending.

Happy Writing!