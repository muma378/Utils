# -*- coding: utf-8 -*-
# word2char.py - usage: python word2char.py dict.txt
# convert a dict of words to chars 
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.June.06

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
			for word, phonetic in separate(items):
				phonetic_dict.setdefault(word, set()).update(phonetic.split('\\'))

	return phonetic_dict

# usually, items are word and phonetic interleaved
# ['国', 'kueq',	 '民', 'min4\min']
def separate(items):
	word, phonetic = '', ''
	for item in items:
		try:
			if item:
				# word is impossible to be decode by ascii
				phonetic = item.decode('ascii')	
				if word:
					yield word, phonetic.strip('\r\n')
					word, phonetic = '', ''
		except UnicodeDecodeError, e:
			word = item

def write_chardict(phonetic_dict):
	with open(single_char_dict, 'w') as f:
		for key, vals in phonetic_dict.items():
			f.write(key)
			vals = filter(lambda x: x, vals)
			f.write('\t' + ' '.join(vals) + '\n')


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