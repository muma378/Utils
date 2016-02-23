# list_all.py - usage: python list_all.py root_dir
# choose the directory which contains a bunch of text with specified name, 
# then extract all text into a file named list_all.txt
# author: Xiaoyang <xiaoyang0117@gmail.com>
# date: 2016.02.05

import os
import sys
import re

LISTTXT_NAME = 'list_all.txt'
NAMEPATTERN = '[a-zA-Z_]*(?P<index>\d+)\.txt'
INDEX_PARSER = re.compile(NAMEPATTERN)


def extract_text(abs_path, textfiles):
	brother_dir = os.path.dirname(abs_path)
	listall_txt = os.path.join(brother_dir, LISTTXT_NAME)
	parent_dir = './' + os.path.basename(abs_path)
	# import pdb;pdb.set_trace()
	with open(listall_txt, 'w') as f:
		# try:
		# 	for filename in textfiles:
		# 		print INDEX_PARSER.match(filename).group('index')
		# except AttributeError, e:
		# 	print filename
		textfiles.sort(key=lambda x: int(INDEX_PARSER.match(x).group('index')))
		
		for filename in textfiles:
			with open(os.path.join(abs_path, filename)) as tf:
				f.write(parent_dir+'/'+filename+os.linesep)
				f.write(tf.read().strip()+os.linesep)


def select_dir(src_dir):
	dirs = [src_dir]
	while len(dirs) != 0:
		_dir = dirs.pop()
		dirs += filter(os.path.isdir, map(lambda x: os.path.join(_dir, x), os.listdir(_dir)))
		textfiles = filter(lambda x: x.endswith('.txt') and INDEX_PARSER.match(x), os.listdir(_dir))
		if len(textfiles) > 0:
			extract_text(_dir, textfiles)

def main():
	select_dir(sys.argv[1])

if __name__ == '__main__':
	main()