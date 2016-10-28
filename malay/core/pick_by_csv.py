# -*- coding: utf-8 -*-

import os
import re
import sys
import csv

def load_csv(filename):
	content = []
	with open(filename, 'rb') as csvfile:
		csvreader = csv.reader(csvfile)
		for row in csvreader:
			content.append(row)
	return content


def read_plain(filename):
	file_dict = {}
	with open(filename, 'r') as f:
		for line in f:
			path = line.strip().decode('gb2312')
			file = re.split(r"\\", path)[-1]
			file_dict[file.replace(" ", "_")] = path
	return file_dict

if __name__ == '__main__':
	filelist = sys.argv[1]
	pickedfile = sys.argv[2]
	files_dict = read_plain(filelist)
	csv_rows = load_csv(pickedfile)
	nameslist = map(lambda x: x[0], csv_rows)
	pathlist = []
	for name in nameslist:
		if files_dict.get(name):
			pathlist.append(files_dict[name])
		else:
			print name
	# pathlist = map(lambda x: files_dict.get(x, "error"), nameslist)
	with open("pathlist.txt", "w") as f:
		for path in pathlist:
			f.write(path.encode("utf-8"))
			f.write('\n')
