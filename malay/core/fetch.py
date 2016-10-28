# -*- coding: utf-8 -*-

import os
import sys
import shutil
from dp.core.base.traverse import traverser

TEMP = 'temp/'

def read_path(plain_file):
	with open(plain_file) as f:
		for path in f:
			yield path.strip()

def fetch(path, dst):
	shutil.copy(path, dst)

# first of all, make sure the original audio size and the to be replaced are the same
# then replace text only
def recover(pathlist, src_dir):
	path_dict = {}
	for path in read_path(pathlist):
		path = win_to_mac_path(path)
		path_dict[os.path.basename(path)] = path

	homo_txt = lambda x: x.replace(".wav", ".txt")
	for src_file, _ in traverser(src_dir, '', '.wav'):
		original = path_dict.get(os.path.basename(src_file))
		# import pdb;pdb.set_trace()
		if not original or not os.path.exists(original):
			print "no matching original files for {0}".format(src_file)
		elif os.stat(original).st_size != os.stat(src_file).st_size:
			print "files {0} have changed since last fetching".format(original)
		else:
			original, src_file = homo_txt(original), homo_txt(src_file)
			if os.path.exists(original):
				shutil.copy(original, TEMP)
				print "{0} was overridden by {1}".format(original, src_file)
				shutil.copy(src_file, original)


def win_to_mac_path(path):
	return path.replace("E:", "/Volumes/E").replace("\\", "/")

if __name__ == '__main__':
	pathlist = sys.argv[1]
	dstdir = sys.argv[2]
	# for path in read_path(pathlist):
	# 	fetch(path, dstdir)
	recover(pathlist, dstdir)