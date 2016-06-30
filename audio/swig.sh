#!/bin/bash

CFLAGS='-fPIC -std=c++11 -c'
swig -c++ -python -o audio_wrap.cpp  audio.i
g++ $CFLAGS audio.cpp common.cpp exceptions.cpp
g++ $CFLAGS audio_wrap.cpp -I/usr/include/python2.7/
g++ -shared audio.o common.o exceptions.o audio_wrap.o -o _audio.so
