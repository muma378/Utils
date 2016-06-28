# -*- coding: utf-8 -*-
import os
import sys
from traverse import traverse_with_extra

def fill(srcfile, _, **kwargs):
	with open(srcfile) as f:
		content = f.read()
	kwargs['slots'].setdefault(content, 0) += 1

def collect(dirlist):
	slots = {}
	for dirname in dirlist:
		traverse_with_extra(dirname, '', fill, target='.txt', slots=slots)

	return slots

if __name__ == '__main__':
	dirlist = sys.argv[1]
	output = sys.argv[2]
	for key, val in collect(dirlist):
		with open(output, 'w') as f:
			f.write(key+'\n')