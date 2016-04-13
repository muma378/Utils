# -*- coding: utf-8 -*-
# classify.py - usage: python classify.py info.txt root
# classify audio into different dir according to its type and date
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.30

import os
import sys
import json
import shutil


FILENAME_KEY = u'文件名'
CARD_CARVE_TYPE = u'卡号类型'
CARD_DATE_TYPE = u'日期'
INVALID_CARD_DATE = u'无'

DIRS_STRUCT = { 
			u"浮凸": {
				u"有日期": "", 
				u"无日期": ""}, 
			u"平面": {
				u"有日期": "",
				u"无日期": ""}
			}
DIRS_KEYS_SEQ = (CARD_CARVE_TYPE, CARD_DATE_TYPE)

VALUE_DIRNAME_MAP = {
	u"无": u"无日期",
	u"有效日期": u"有日期",
	u"制卡日期": u"有日期",
	u"发卡日期": u"有日期",
	u"不确定": u"有日期",
	u"浮凸": u"浮凸",
	u"平面": u"平面"
}

CODING = 'gb2312'

for key, val in VALUE_DIRNAME_MAP.items():
	VALUE_DIRNAME_MAP[key] = val.encode(CODING)

def classify(info_dict, root):
	filelist = get_filelist(root)

	for filename in filelist:
		try:
			basename = os.path.basename(filename)
			info = info_dict[basename]
		except KeyError, e:
			print basename.decode(CODING) + u" is not in the list"
			continue

		try:
			filepath = root
			for dir_key in DIRS_KEYS_SEQ:
				dirname = VALUE_DIRNAME_MAP[info[dir_key]]
				filepath = os.path.join(filepath, dirname)
		except KeyError, e:
			print u"unable to recognize info " + info[dir_key] + u" for file: " + filename
			continue

		if os.path.exists(filepath):
			new_filepath = os.path.join(filepath, basename)
			if filename != new_filepath:
				if os.path.exists(new_filepath):
					print new_filepath + " that " + filename+ " will be moved to has already existed"
				else:
					print "moved to " + new_filepath + " from " + filename
				shutil.move(filename, new_filepath)
		else:
			print "path " + filepath + " is not exist"
			continue

def get_filelist(root, target='.jpg'):
	filelist = []
	# return os.listdir(root)
	for dirpath, dirnames, filenames in os.walk(root):
		for filename in filenames:
			if filename.endswith(target):
				src_file = os.path.join(dirpath, filename)
				filelist.append(src_file)
	return filelist

def construct_dirs(root, dirs_struct):
	for sub_dir in traverse_dict(dirs_struct):
		dirs = os.path.join(root, sub_dir.encode(CODING))
		if not os.path.exists(dirs):	
			os.makedirs(dirs)

def traverse_dict(dirs_struct):
	assert(type(dirs_struct) == dict)
	for parent, child in dirs_struct.items():
		if not child:
			yield parent
		else:
			for descendant in traverse_dict(child):
				yield os.path.join(parent, descendant)


def hashing(info_txt):
	info_dict = {}
	with open(info_txt,'r') as f:
		for line in f:
			info = json.loads(line)
			try:
				basename = os.path.basename(info[FILENAME_KEY])
				info_dict[basename] = info
			except KeyError, e:
				print "unable to find key " + FILENAME_KEY + " in " + line
	return info_dict

def main(info_txt, root):
	info_dict = hashing(info_txt)
	construct_dirs(root, DIRS_STRUCT)

	classify(info_dict, root)

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "python " + sys.argv[0] + "info.txt dirname"
		sys.exit(1)
	info_txt = sys.argv[1]
	root = sys.argv[2]
	main(info_txt, root)
