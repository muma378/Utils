# -*- coding: utf-8 -*-
# rank_segmented.py - usage: python rank_segmented.py filename
# to extract a specified phrase, then segment it and rank by the frequency of appearance
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Aug.11

import re
import sys

from common import parse
from common import utils


# to extract a phrase which started with a marker in each line, to segment then
def extract_interpretor(line, marker="A ?:"):
	line = re.sub("^.*"+marker, "", line)
	words_list = utils.segment(line)
	for word in words_list:
		try:
			word.encode('utf-8').decode("ascii")	# check to see if it was only can be decoded by utf-8 
		except UnicodeDecodeError, e:
			yield word, 1	# only yield when it was chinese characters

def accumulate_loader(loaded_dict, k, v):
	return loaded_dict.get(k, 0) + v

if __name__ == '__main__':
	filename = sys.argv[1]
	frequency_dict = parse.loads_dict(filename, extract_interpretor, accumulate_loader)
	utils.rank_by_freq(frequency_dict, filename)