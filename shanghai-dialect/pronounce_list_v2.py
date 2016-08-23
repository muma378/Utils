# -*- coding: utf-8 -*-
# pronounce_list_v2.py - usage: python pronounce_list_v2.py dict_file src_file
# extracts words from src_file to generate a list which containing words and corresponding phonetic
# if the word was not able be found in the dict, it would be appended at the end of the file
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Aug.24


import os
import sys
import re
from common import parse
from common import utils
from common.utils import unicode_split, spell

# concatenate each part untill words ended with numbers
# ['b', 'o1', 'l', 'i5', 'zh', 'ix3']
# => ['b o1', 'l i5', 'zh ix3']
def num_ended_concatenater(words, gap=' '):
	result = ['']
	for word in words:
		word = word.strip()
		if word:
			result[-1] +=  word
			if re.search('\d$', word):
				result.append('')
			else:
				result[-1] +=  gap
	result.pop()	# pop the last pushing
	return result


def extract_words(src_file, column_no):
	words = set()
	with open(src_file) as f:
		for line in f:
			words.update(unicode_split(line.split('\t')[column_no].strip(), 'utf-8'))
			# import pdb;pdb.set_trace()
	return words


if __name__ == '__main__':
	dict_file = sys.argv[1]
	source_file = sys.argv[2]
	interpretor = lambda x: parse.continual_words_interpretor(x, concatenater=num_ended_concatenater)
	reference = parse.loads_dict(dict_file, interpretor, parse.set_loader)
	reference = {k : ' '.join(v) for k,v in reference.iteritems()}

	words = extract_words(source_file, 3)
	target_file = source_file+'.list'
	unreferenced = spell(words, reference, target_file)
	with open(target_file, 'a') as f:
		for word in unreferenced:
			if not utils.is_ascii(word):
				if utils.is_gb2312(word):
					f.write(word)
					f.write('\n')

