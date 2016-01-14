import os
import sys
import re
import shutil

path_pattern = '.*\\\\Body\\\\.*'

def matchfiles(search_dir, dst_dir, filelist, path_pattern):
	path_parser = re.compile(path_pattern)
	for dirpath, dirnames, filenames in os.walk(search_dir):
		if path_parser.match(dirpath):
			for filename in filenames:
				if filename in filelist:
					shutil.copy(os.path.join(dirpath, filename), dst_dir)

def get_filelist(src_dir):
	return os.listdir(src_dir)

if __name__ == '__main__':
	src_dir, search_dir, dst_dir = sys.argv[1:3]
	filelist = get_filelist(src_dir)
	matchfiles(search_dir, dst_dir, filelist, path_pattern)