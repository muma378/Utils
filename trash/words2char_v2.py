# -*- coding: utf-8 -*-
# word2char_v2.py - usage: python word2char.py dict.txt
# convert a dict of words to chars 
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.July.04

import os
import sys
import re

single_char_dict = "single_char_dic.txt"
single_char_list = "single_char_lst.txt"

def loads_dict(dict_file):
	phonetic_dict = {}
	with open(dict_file, 'r') as f:
		for line in f:
			items = re.split('\t| ', line)
			for word, phonetic in aggregate(items):
				phonetic_dict.setdefault(word, set()).update(phonetic.split('\\'))

	return phonetic_dict


# all phonetic are listed in a single line
# ['觉', 'c', 'i', 'oq2', '\k', 'oq1', '\k', 'o1']
# which means {'觉': set('cioq2', 'koq1', 'ko1')}
def aggregate(items):
	yield items[0], ''.join(items[1:]).strip('\n')


def write_chardict(phonetic_dict):
	with open(single_char_dict, 'w') as f:
		for key, vals in phonetic_dict.items():
			f.write(key)
			vals = filter(lambda x: x, vals)
			f.write('\t' + '\\'.join(vals) + '\n')


def write_charlist(phonetic_dict):
	with open(single_char_list, 'w') as f:
		for key, vals in phonetic_dict.items():
			vals = filter(lambda x: x, vals)
			for val in vals:
				f.write(val + '\n')

if __name__ == '__main__':
	dict_file = sys.argv[1]
	phonetic_dict = loads_dict(dict_file)
	write_chardict(phonetic_dict)
	# write_charlist(phonetic_dict)