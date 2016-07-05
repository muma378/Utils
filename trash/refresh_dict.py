# refresh_dict.py - usage: python refresh_dict.py old_word_dict.txt new_char_dict.txt
# replace words in the old dict with new ones
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.July.04

import os
import sys
import re


def loads_dict(filename, interpretor):
	loaded_dict = {}
	with open(filename, 'r') as f:
		for line in f:
			for key, val in interpretor(line):
				loaded_dict.setdefault(key, set()).update(val)
	return loaded_dict


def chars_interpretor(line):
	items = line.split('\t')
	if len(items) == 1:
		yield items[0], ''
	elif len(items) == 2:
		yield items[0], items[1].strip('\n').split('\\')
	else:
		yield items[0], ''.join(items[1:]).strip('\n').split('\\')


def normalize(loaded_dict):
	for key, val in loaded_dict.items():
		loaded_dict[key] = '\\'.join(sorted(list(val)))
	return loaded_dict


def words_interpretor(line):
	items = re.split('\t| ', line)
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


def scan_and_replace(old_word_dict, reference):
	with open('new_'+old_word_dict, 'w') as w:
		with open(old_word_dict) as f:
			for line in f:
				phrase_list = []
				for word, phonetic in words_interpretor(line):
					phrase_list.append(word + ' ' + reference.get(word, phonetic))
				w.write('\t'.join(phrase_list) + '\n')


if __name__ == '__main__':
	old_word_dict = sys.argv[1]
	new_char_dict = sys.argv[2]
	reference = loads_dict(new_char_dict, chars_interpretor)
	reference = normalize(reference)
	scan_and_replace(old_word_dict, reference)



