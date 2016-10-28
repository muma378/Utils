# -*- coding: utf-8 -*-
# utf8ize.py - usage: python utf8ize.py root_dir
# to decode all text files in root_dir and encoding with utf-8
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Feb.26
import os
import sys
import re
import chardet

from traverse import traverse

# sub_parser = re.compile('^([\s\w]+?\.pcm\s*\n)+', re.MULTILINE)
blank_parser = (re.compile('^.*\.pcm\s*\n', re.MULTILINE), '')	# remove line with pcm and empty ones

# remove lines with pcm names and insert correct names into the first line
def encode(src_file, _):
	with open(src_file, 'rb') as f:
		raw_data = f.read()
		coding = chardet.detect(raw_data)['encoding']

	if coding != 'utf-8-sig':
		data = raw_data.decode(coding)
		with open(src_file, 'w') as f:
			f.write(data.encode('utf-8-sig'))
			print("encoded %s from %s " % (src_file, coding))


def main():
	root_dir = sys.argv[1]
	traverse(root_dir, '', encode, '.txt')


if __name__ == '__main__':
	main()