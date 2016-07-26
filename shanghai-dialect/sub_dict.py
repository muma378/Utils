# -*- coding: utf-8 -*-
# extract_dict.py - usage: python extract_dict.py dict_name.txt content.txt
# extract a subset of dict, which only contains characters in content.txt
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Jul.26

import os
import sys
import parse
import utils


def read_content(content_file):
	def interpretor(line):
		items = line.split('\t')
		chars = []
		if len(items) == 3:
			chars = utils.unicode_split(utils.clean(items[2]), 'utf-8')
		else:
			print "error: number of items is not correct - "
			print line

		for single_char in chars:
			yield single_char

	chars_set = set()
	with open(content_file, 'r') as f:
		for line in f:
			for single_char in interpretor(line):
				chars_set.add(single_char)

	return chars_set


if __name__ == '__main__':
	dictname = sys.argv[1]
	content_file = sys.argv[2]
	loaded_dict = parse.loads_dict(dictname, parse.simple_interpretor, parse.default_loader)
	chars_set = read_content(content_file)
	utils.spell(chars_set, loaded_dict, dictname+'.dict')