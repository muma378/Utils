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


def main():
	diff(sys.argv[1], sys.argv[2], lambda x:x.replace('.wav', ''), lambda x:x.replace('.textgrid', ''))


if __name__ == '__main__':
	main()