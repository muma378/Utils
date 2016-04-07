# -*- coding: utf-8 -*-
# unique_files.py - usage: python unique_files.py target_dir
# lists all files exised in other directories, only keeps the first one scanned
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.10

import os
import sys
from traverse import traverse

slots = {}
duplicated = {}

def collect(file_path, _):
	filename = os.path.basename(file_path)
	if slots.get(filename, None):
		root = get_root(file_path)
		duplicated.setdfault(root, []).append(file_path)
	else:
		slots[filename] = file_path


def get_root(file_path):
	return '.' + os.sep + file_path.replace(abs_target, '').split(os.sep)[0]

def prints(filename):
	with open(filename, 'w') as f:
		for key, vals in duplicated.items():
			f.write(os.linesep)
			f.write(key)
			f.writes('saved:'+slots[key])
			f.writes('to delete:'+os.linesep)
			for val in vals:
				f.write('\t' + val)


def main(target):
	traverse(target, '', collect, '.wav')
	

if __name__ == '__main__':
	target_dir = sys.argv[1]
	abs_target = os.path.abspath(target_dir)
	abs_target = abs_target if abs_target.endswith(os.sep) else abs_target+os.sep
