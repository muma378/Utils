# -*- coding: utf-8 -*-
# provides different interpretors to load dict
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.July.26

import os
import sys
import re
from common.utils import unicode_split, is_ascii


CODING = 'utf-8'

default_loader = lambda d, k, v: v

def set_loader(d, k, v):
	d.setdefault(k, set()).add(v)
	return d.get(k)


def loads_dict(filename, interpretor, loader=default_loader):
	loaded_dict = {}
	with open(filename, 'r') as f:
		for line in f:
			for key, val in interpretor(line):
				if val:
					loaded_dict[key] = loader(loaded_dict, key, val)
	return loaded_dict

# only to extract the first character to be the key
# eg. 
# 步	b	u2
# 簿	b	oq	\b	u
# => {"步":"b	u2", "簿":"b	oq	\b	u"}
def simple_interpretor(line):
	items = line.split('\t')
	if len(items) == 1:
		print line
		yield items[0], ''
	elif len(items) > 1:
		yield items[0], line.replace(items[0], '').strip()
	

# chars were ought to be displayed as:
# 歼	tzi1
# 圹	khuaon3
# 圾	sij4\seq4
# => {"歼":"tzj1"}
def chars_interpretor(line):
	items = line.split('\t')
	if len(items) == 1:
		yield items[0], ''
	elif len(items) == 2:
		yield items[0], items[1].strip('\n').split('\\')
	else:
		yield items[0], ''.join(items[1:]).strip('\n').split('\\')


# used in scan_and_replace
# case for "上 zaon2\lan2		午 ng\wu1"
# => {"上":"zaon2\lan2", "午": "ng\wu1"}
def isolated_words_interpretor(line, sep='\t| '):
	items = re.split(sep, line)
	word, phonetic = '', ''
	for item in items:
		try:
			if item:
				# word is impossible to be decode by ascii
				phonetic = item.decode('ascii')	
				if word:
					yield word, phonetic.strip()
					word, phonetic = '', ''
		except UnicodeDecodeError, e:
			word = item

# used in scan_and_replace
# case for "上午	zaon2\lan2 ng\wu1"
# => {"上":"zaon2\lan2", "午": "ng\wu1"}
def continual_words_interpretor(line, word_sep=' ', phonetic_sep=' ', concatenater=None):
	items = re.split(word_sep, line)
	
	if len(items) == 2:
		phonetic_line = items[1]
	elif len(items) > 2:
		rest_part = word_sep.join(items[1:])
		if is_ascii(rest_part):
			phonetic_line = rest_part
		else:
			print "warning: number of items is incorrect - "
			print line
	else:
		print "seprator for words and phonetics is not correct - "
		print line

	if phonetic_line:
		words = unicode_split(items[0], CODING)
		phonetic = phonetic_line.split(phonetic_sep)
		if concatenater:
			phonetic = concatenater(phonetic)

		if len(words) == len(phonetic):
			for char, phone in zip(words, phonetic):
				yield char, phone
		else:
			print "warning: word and phonetic are not matched - "
			print line		


