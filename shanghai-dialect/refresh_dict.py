# -*- coding: utf-8 -*-
# refresh_dict.py - usage: python refresh_dict.py old_word_dict.txt new_char_dict.txt
# replace words in the old dict with new ones
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.July.04

import os
import sys
import re


CODING = 'utf-8'

def loads_dict(filename, interpretor):
	loaded_dict = {}
	with open(filename, 'r') as f:
		for line in f:
			for key, val in interpretor(line):
				loaded_dict.setdefault(key, set()).update(val)
	return loaded_dict

# chars were ought to be displayed as:
# 歼	tzi1
# 圹	khuaon3
# 圾	sij4\seq4
def chars_interpretor(line):
	items = line.split('\t')
	if len(items) == 1:
		yield items[0], ''
	elif len(items) == 2:
		yield items[0], items[1].strip('\n').split('\\')
	else:
		yield items[0], ''.join(items[1:]).strip('\n').split('\\')

# sort and concatenate phonetic
def normalize(loaded_dict):
	for key, val in loaded_dict.items():
		loaded_dict[key] = '\\'.join(sorted(list(val)))
	return loaded_dict


# case for "上 zaon2\lan2		午 ng\wu1"
def isolated_words_interpretor(line):
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


def unicode_split(text, coding):
	unicode_text = text.decode(coding)
	chars = []
	for char in unicode_text:
		chars.append(char.encode(coding))
	return chars


# case for "上午	zaon2\lan2 ng\wu1"
def continual_word_interpretor(line):
	items = re.split('\t', line)

	if len(items) == 2:
		words = unicode_split(items[0], CODING)
		# import pdb;pdb.set_trace()
		phonetic = items[1].split(' ')
		if len(words) == len(phonetic):
			for char, phone in zip(words, phonetic):
				yield char, phone
		else:
			print "warning: word and phonetic are not matched - "
			print line
	else:
		print "warning: items are not intact - "
		print line

	


# replace phonetic in the old_word_dict with new ones in the reference
def scan_and_replace(old_word_dict, reference, words_interpretor):
	new_word_dict = os.path.join(os.path.dirname(old_word_dict), 'new_'+os.path.basename(old_word_dict))
	with open(new_word_dict, 'w') as w:
		with open(old_word_dict) as f:
			for line in f:
				phrase_list = []

				for word, phonetic in words_interpretor(line.strip()):
					# phrase_list.append(word + ' ' + reference.get(word, phonetic))
					if phrase_list:
						phrase_list[0] = phrase_list[0]+word
						phrase_list[1] = phrase_list[1]+' '+reference.get(word, phonetic)
					else:
						phrase_list.append(word)
						phrase_list.append(reference.get(word, phonetic))
				w.write('\t'.join(phrase_list) + '\n')


if __name__ == '__main__':
	old_word_dict = sys.argv[1]
	new_char_dict = sys.argv[2]
	reference = loads_dict(new_char_dict, chars_interpretor)
	reference = normalize(reference)
	scan_and_replace(old_word_dict, reference, continual_word_interpretor)



