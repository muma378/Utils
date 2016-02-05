# -*- coding: utf-8 -*-
import os
import sys
import re
import shutil
from traverse import traverse

NAME_PATTERN = '^OldMan(?P<start>\d+)-\d+_(?P<index>\d+)_?[0-9._]*\.(?P<type>(txt)|(wav))$'
name_parser = re.compile(NAME_PATTERN)

def flatten(src_file, dst_file):
	global name_parser
	basename = os.path.basename(dst_file)
	r = name_parser.match(basename)
	if r:
		basename = 'OldMan'+str(int(r.group('start'))+int(r.group('index'))-1)+'.'+r.group('type')
		dst_file = os.path.join(dst_file.split(os.sep)[0], basename)
		shutil.copy(src_file, dst_file)
	else:
		print('Unabel to match %s' % basename)

def main():
	traverse(sys.argv[1], sys.argv[2], flatten, target='')

if __name__ == '__main__':
	main()
