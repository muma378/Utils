# -*- coding: utf-8 -*-
# join_dirs.py - usage: python join_dirs.py info.txt root
# correct names indicated in info.txt, use relative names instead of filename only
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.30

import os
import sys
import json
import classify as cf
from traverse import traverse

def correct_names(src_file, _):
	filename = os.path.basename(src_file)
	try:
		# print os.path.relpath(src_file, root)
		info_dict[filename][cf.FILENAME_KEY] = os.path.relpath(src_file, root).decode('utf-8')
	except KeyError, e:
		print u"unable to find file " + filename + u" in the info.txt "


def main(info_txt, root):
	traverse(root, '', correct_names, target='.jpg')
	with open(info_txt+'.bak', 'w') as f:
		for info in info_dict.values():
			f.write(json.dumps(info, ensure_ascii=False).encode('utf-8'))
			f.write(os.linesep)


if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "python " + sys.argv[0] + "info.txt dirname"
		sys.exit(1)
	info_txt = sys.argv[1]
	root = sys.argv[2]

	info_dict = cf.hashing(info_txt)
	main(info_txt, root)
