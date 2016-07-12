# -*- coding: utf-8 -*-
# word2char_v2.py - usage: python word2char.py dict.txt
# convert a dict of words to chars 
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.July.04

import os
import sys
import re

diff_result_txt = "diff_result.txt"

def loads_dict(dict_file):
	phonetic_dict = {}
	with open(dict_file, 'r') as f:
		for line in f:
			items = re.split('\t', line)
			for word, phonetic in detach(items):
				phonetic_dict.setdefault(word, set()).update(phonetic.split('\\'))
	return phonetic_dict


def detach(items):
	if len(items) == 1:
		yield items[0], ''
	elif len(items) == 2:
		yield items[0], items[1].strip('\n')
	else:
		yield items[0], ''.join(items[1:]).strip('\n')


def diff(dict1, dict2):
	with open(diff_result_txt, 'w') as f:
		for key, val in dict1.items():
			if val != dict2.get(key):
				f.write(key + '\t' + '\\'.join(val) + '\t' + '\\'.join(dict2.get(key)) + '\n')


if __name__ == '__main__':
	phonetic_dict = loads_dict(sys.argv[1])
	phonetic_dict2 = loads_dict(sys.argv[2])
	diff(phonetic_dict, phonetic_dict2)