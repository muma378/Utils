# -*- coding: utf-8 -*-
# exclude.py - usage: python exclude.py all.txt subset.txt
# excludes text in subset.txt from all.txt
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Oct.14

import os
import sys
from multiprocessing import Pool

def load_subset(subset_file):
	allocated = {}
	with open(subset_file) as f:
		for line in f:
			line = line.strip()
			if line:
				allocated[line] = 1
	return allocated

def exclude(all_file, new_file, allocated):
	with open(new_file, 'w') as new:
		with open(all_file, 'r') as f:
			trial = 0
			while True:
				lines = f.readlines(5000)
				if not lines:
					if trial > 1:
						break
					else:
						# import pdb;pdb.set_trace()
						f.readline()
						trial += 1	#try again
						continue
				
				for line in lines:
					if allocated.get(line.strip()):
						# print('{0} was allocated before, skipped'.format(line.strip().decode('utf-8').encode('gb2312')))
						continue
					new.write(line)
				trial = 0

def main(subset_file):
	all_file = sys.argv[1]
	subset_file_name = os.path.basename(subset_file)
	all_file_path = os.path.dirname(all_file)
	new_file = os.path.join(all_file_path, u'无'.encode('gb2312')+subset_file_name)

	allocated = load_subset(subset_file)
	exclude(all_file, new_file, allocated)


if __name__ == '__main__':
	all_file = sys.argv[1]
	subset_dir = sys.argv[2]
	main(subset_dir)

	# subset_files = map(lambda p: os.path.join(subset_dir, p), filter(lambda x: x.endswith('.txt'), os.listdir(subset_dir)))
	
	# args = [ (all_file, sub) for sub in subset_files ]
	# p = Pool(4)
	# p.map(main, subset_files)
