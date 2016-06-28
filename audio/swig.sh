#!/bin/bash

swig -c++ -python audio.i
g++ -fPIC -c common.cpp audio_wrap.cpp -I/usr/include/python2.7/
g++ -shared common.o audio_wrap.o -o audio.so
