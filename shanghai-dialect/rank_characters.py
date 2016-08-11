# rank_by_freq - usage: python rank_by_freq filename
# get times characters appeared in a file, and list them in ascending
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Aug.05


import os
import sys
from collections import OrderedDict
from common.utils import rank_by_freq, unicode_split

CODING = 'utf-8'


def list_phrase(phrase_list, filename):
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


if __name__ == '__main__':
	filename = sys.argv[1]
	frequency_dict, phrase_list = statistic(filename)
	rank_by_freq(frequency_dict, filename)
	list_phrase(phrase_list, filename)
