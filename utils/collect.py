# collect.py - usage: python collect.py file.txt
# collect all content after the first column
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Jun.27

import os
import sys
import re

def collect(filename):
	collections = set()
	with open(filename, 'r') as f:
		for line in f:
			collections.update(map(lambda x: x.replace('\\', ''), filter(lambda x: x.strip(), line.split('\t')[1:-1])))
	import pdb;pdb.set_trace()
	with open('uniq_'+filename, 'w') as f:
		for chars in collections:
			f.write(chars)
			f.write('\n')


def main(filename):
	collect(filename)
	

if __name__ == '__main__':
	filename = sys.argv[1]
	main(filename)