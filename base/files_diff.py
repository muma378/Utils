# files_diff.py - usage: python files_diff.py dir1 dir2
# compares files existed in two directories and outputs the difference
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Jan.25

import os
import sys
from difflib import Differ

OUTPUT_FILE = 'diff.txt'

def diff(dir1, dir2, fn1, fn2):
	filenames_list1 = sorted(map(fn1, os.listdir(dir1)))
	filenames_list2 = sorted(map(fn2, os.listdir(dir2)))

	df = Differ()
	result = df.compare(filenames_list1, filenames_list2)
	with open(OUTPUT_FILE, 'w') as f:
		f.write('\n'.join(result))

# compare files listed in the same directory but with different suffix
def diff_inside(_dir, type1, type2):
	files =  os.listdir(_dir)
	filenames_list1 = sorted(map(lambda x:x.replace(type1, ''), filter(lambda f: f.endswith(type1), files)))
	filenames_list2 = sorted(map(lambda x:x.replace(type2, ''), filter(lambda f: f.endswith(type2), files)))

	df = Differ()
	result = df.compare(filenames_list1, filenames_list2)
	with open(OUTPUT_FILE, 'w') as f:
		f.write('\n'.join(result))


if __name__ == '__main__':
	# diff(sys.argv[1], sys.argv[2], lambda x:x.replace('.wav', ''), lambda x:x.replace('.textgrid', ''))
	diff_one(sys.argv[1], '.wav', '.txt')
