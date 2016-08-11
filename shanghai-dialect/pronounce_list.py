# -*- coding: utf-8 -*-
# list all phonetic
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Jul.26

import re
import sys
import parse

phonetic_set = set()

def collect_phonetic_loader(dic, key, val):
	global phonetic_set
	map(lambda x: phonetic_set.add(re.sub('\d|\\\\', '', x)), val.strip().split('\t'))
	return val

if __name__ == '__main__':
	dictname = sys.argv[1]
	loaded_dict = parse.loads_dict(dictname, parse.simple_interpretor, collect_phonetic_loader)
	with open(dictname+'.list', 'w') as f:
		for phonetic in phonetic_set:
			f.write(phonetic+'\n')