# -*- coding: utf-8 -*-
# utils for shanghai-dialect
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Jul.26

import re
from collections import OrderedDict


# load a dict with an interpretor to "explain" each line
def read(filename, interpretor):
	with open(filename, 'r') as f:
		for line in f:
			for key, val in interpretor(line):
				loaded_dict.setdefault(key, set()).update(val)
	return loaded_dict

# sort and concatenate phonetic
def normalize(loaded_dict):
	for key, val in loaded_dict.items():
		loaded_dict[key] = '\\'.join(sorted(list(val)))
	return loaded_dict


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
						phrase_list[0] = phrase_list[0] + word
						phrase_list[1] = phrase_list[1] + ' ' + reference.get(word, phonetic)
					else:
						phrase_list.append(word)
						phrase_list.append(reference.get(word, phonetic))
				w.write('\t'.join(phrase_list) + '\n')



# case for "上 zaon2\lan2		午 ng\wu1"
# => {"上":"zaon2\lan2", "午": "ng\wu1"}
def isolated_words_interpretor(line):
	items = re.split('\t| ', line)
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


# case for "上午	zaon2\lan2 ng\wu1"
# => {"上":"zaon2\lan2", "午": "ng\wu1"}
def continual_word_interpretor(line):
	items = re.split('\t', line)
	
	if len(items) == 2:
		words = unicode_split(items[0], CODING)
		phonetic = items[1].split(' ')
		if len(words) == len(phonetic):
			for char, phone in zip(words, phonetic):
				yield char, phone
		else:
			print "warning: word and phonetic are not matched - "
			print line
	else:
		print "warning: number of items is incorrect - "
		print line

# split characters encoded in utf-8
def unicode_split(text, coding):
	unicode_text = text.decode(coding)
	chars = []
	for char in unicode_text:
		chars.append(char.encode(coding))
	return chars


def look_up(word, pronounce_dict):
	word = word.strip()
	pronounce_list = []
	for letter in word:
		pronounce_list.append(pronounce_dict[letter])

	return word + '\t' + ' '.join(pronounce_list)+os.linesep


# removes all [s], [t] and letters wrapped with []
def clean(line):
	return re.sub("\[.\]", '', line)


# segment words with library jieba
def segment(line):
	import jieba
	seg_list = jieba.cut(line, cut_all=False)
	return filter(lambda x: x.strip(), seg_list)

# output words listed in container (could be set, list, or other iterative objects)
# and corresponding phonetic in the reference (ought to be a dict) 
def spell(container, reference, filename):
	with open(filename, 'w') as f:
		for item in container:
			if reference.get(item):
				f.write(item)
				f.write('\t'+reference[item]+'\n')
			else:
				print item


# sort a dict by words' frequency 
def rank_by_freq(frequency_dict, filename, coding='utf-8', reverse=False):
	freqs = OrderedDict(sorted(frequency_dict.items(), key=lambda x: x[1], reverse=reverse))
	with open(filename + '.feq', 'w') as f:
		for k, n in freqs.items():
			f.write(k.encode(coding))
			f.write('\t'+str(n)+'\n')

	