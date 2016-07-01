#!/usr/bin/env python

"""
setup.py for audio processing library
"""
import os
from distutils.core import setup, Extension

audio_module = Extension('_audio', 
                         sources=['audio_wrap.cpp', 'audio.cpp', 'common.cpp', 'exceptions.cpp'],
                         extra_compile_args=['-std=c++11', ]
                         )
os.environ["CC"] = "g++"
setup (name = 'audio',
        version = '1.0',
        author = 'Yang',
        description = "provides simple interfaces to process audio",
        ext_modules = [audio_module],
        py_modules = ["audio"],
        )
