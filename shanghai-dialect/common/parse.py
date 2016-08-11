# -*- coding: utf-8 -*-
# provides different interpretors to load dict
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.July.26

import os
import sys
import re


CODING = 'utf-8'

set_loader = lambda d, k, v: d.setdefault(k, set()).update(v).get(k)
default_loader = lambda d, k, v: v


def loads_dict(filename, interpretor, loader):
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


