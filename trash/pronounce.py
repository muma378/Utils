# -*- coding: utf-8 -*-
# replace word started without # with its pronounce
import os
import sys

UNPRONOUNCE_MARK = "#"

def loads_dict(dict_file):
	pronounce_dict = {}
	with open(dict_file, 'r') as f:
		for line in f:
			items = line.split('\t')
			key = items[0].strip()
			pronounce = '\t'.join(items[1:]).strip()
			pronounce_dict[key] = pronounce

	return pronounce_dict

def look_up(word, pronounce_dict):
	word = word.strip()
	pronounce_list = []
	for letter in word:
		pronounce_list.append(pronounce_dict[letter])

	return word + '\t' + ' '.join(pronounce_list)+os.linesep

def read_words(words_file, pronounce_dict):
	words_list = []
	with open(words_file, 'r') as f:
		for i, word in enumerate(f, start=1):
			if not word.startswith(UNPRONOUNCE_MARK):
				try:
					words_list.append(look_up(word, pronounce_dict))
				except KeyError, e:
					print "unable to find key " + word + " at line " + str(i)

	return words_list

def write_words(words_file, words_list):
	with open(words_file, 'w') as f:
		for word in words_list:
			f.write(word)


def main(words_file, dict_file):
	pronounce_dict = loads_dict(dict_file)
	words_list = read_words(words_file, pronounce_dict)
	write_words(words_file+'.new', words_list)

if __name__ == '__main__':
	dict_file = sys.argv[1]
	words_file = sys.argv[2]
	main(words_file, dict_file)
