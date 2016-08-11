# rank_by_freq - usage: python rank_by_freq filename
# get times characters appeared in a file, and list them in ascending
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Aug.05


import os
import sys
from collections import OrderedDict


CODING = 'utf-8'

def rank_by_freq(frequency_dict):
	global filename
	freqs = OrderedDict(sorted(frequency_dict.items(), key=lambda x: x[1]))
	with open(filename + '.feq', 'w') as f:
		# import pdb;pdb.set_trace()
		for k, n in freqs.items():
			f.write(k)
			f.write('\t'+str(n)+'\n')

def list_phrase(phrase_list):
	global filename
	with open(filename + '.phrase', 'w') as f:
		for line in phrase_list:
			f.write(line)

def statistic(filename):
	frequency_dict = {}		# charachters and corresponding frequency
	phrase_list = []	# append if the length was less than 10
	with open(filename, 'r') as f:
		for line in f:
			chars = filter(lambda x: x.strip(), unicode_split(line, CODING))
			if len(chars) <= 10:
				phrase_list.append(line)
			for char in chars:
				frequency_dict[char] = frequency_dict.get(char, 0) + 1
	return frequency_dict, phrase_list


def unicode_split(text, coding):
	unicode_text = text.decode(coding)
	chars = []
	for char in unicode_text:
		chars.append(char.encode(coding))
	return chars


if __name__ == '__main__':
	filename = sys.argv[1]
	frequency_dict, phrase_list = statistic(filename)
	rank_by_freq(frequency_dict)
	list_phrase(phrase_list)