# -*- coding: utf-8 -*-
# multi_split.py - usage: python multi_split.py wave_dirs text_dirs
# for Panasonic emotions
# split wav files into pieces according to multiple text files
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.April.12


import os
import re
import sys
import pairwise
import traverse
import split

DECODING = 'gb2312' if os.name=='nt' else 'utf-8'
EMOTION_PARSER = re.compile(u"情感英语.*\W(\w*)\.txt", re.UNICODE)
# put all files and corEMOresponding location into a dict
def collect_files(src_file, _, **kwargs):
	basename = os.path.basename(src_file)
	kwargs['use_dict'][basename] = src_file


def main(wave_dirs, text_dirs):
	wave_dict = {}
	traverse.traverse_with_extra(wave_dirs.encode(DECODING), '', collect_files, target='.wav', use_dict=wave_dict)
	text_dict = {}
	traverse.traverse_with_extra(text_dirs.encode(DECODING), '', collect_files, target='.txt', use_dict=text_dict)
	text_keys, wave_keys = text_dict.keys(), wave_dict.keys()
	# excludes the exactly same at first
	pairs = []
	# pairs = pairwise.exclude_same_pairs(text_keys, wave_keys, map_fns=[lambda x: '', lambda x: x.replace('.txt', '.wav')])
	# try to match similar ones
	pairs = pairwise.get_pairs(text_keys, wave_keys, pairs=pairs, use_cache=True)
	
	for text, wave in pairs:
		try:
			emotion_tag = EMOTION_PARSER.match(text.decode(DECODING)).group(1)	# happy, sad, angry ...
			parent_dir = os.path.basename(os.path.dirname(wave_dict[wave])).decode(DECODING)
		except AttributeError, e:
			print "unable to extact emotion tag for filename: " + text

		try:
			dst_dir = os.path.join(text_dirs, parent_dir, emotion_tag)
			split.split_by_cols(text_dict[text], wave_dict[wave], dst_dir=dst_dir, name_prefix=emotion_tag+'_')
		except ValueError, e:
			print "unable to split wav as " + text_dict[text] 


if __name__ == '__main__':
	wave_dirs = sys.argv[1].decode(DECODING)
	text_dirs = sys.argv[2].decode(DECODING)
	main(wave_dirs, text_dirs)
