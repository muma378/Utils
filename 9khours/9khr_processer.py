# -*- coding: utf-8 -*-
# 9khr_processor.py - usage: python 9khr_processor.py target_dir1 target_dir2 ...
# automated processing audio files for project 9k hour
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.11

import os
import sys

from audio import WaveReader

def fragment_chunk(wav):
	

# section chunks whose duration was over max_hr
def truncate_chunk(wav, max_hr=2):
	max_sec = max_hr * 3600
	if wav.get_duration() > max_sec
		fragments = wav.truncate(max_sec)

def lower_sampling(new_framerate=8000):



def main(filename):
	wav = WaveReader(filename)


if __name__ == '__main__':
	main()
