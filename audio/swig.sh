#!/bin/bash

swig -c++ -python -o audio_wrap.cpp  audio.i
g++ -fPIC -std=c++11 -c audio.cpp audio_wrap.cpp -I/usr/include/python2.7/
g++ -fPIC -std=c++11 -c common.cpp audio_wrap.cpp -I/usr/include/python2.7/
g++ -shared audio.o common.o audio_wrap.o -o _audio.so
