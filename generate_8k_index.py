#-*- coding:utf-8 -*-
import os
import sys
import re
import time
import collections
from subprocess import Popen


# audio settings
AS = {
	'header' : 44,
	'samplerate': 16000,
	'bitrate': 16,
	'channel': 1
}


# TODO: to print the error traceback
def exit_prompt(msg):
	print msg
	time.sleep(2)
	sys.exit(0)

def validate(*args):
	mkdir = 'MD' if os.name is 'nt' else 'mkdir'
	for arg in args:
		if not os.path.exists(arg):
			reply = raw_input("Can not find %s, do you want to create a directory named it? [Y/N]" % arg)
			if reply.lower() is "n" or "no":
				exit_prompt("You choosed no, exit now ...")
			else:
				Popen([mkdir, arg])
				print("Directory %s is created." % arg)

# files matched pattern in the path rooted src are fetched and moved to the dst
def fetch_files(src, dst='temp', pattern='.*\.8K'):
	validate(src, dst)
	prog = re.compile(pattern, re.UNICODE)
	for dirpath, dirnames, filenames in os.walk(src):
		for filename in filenames:
			if prog.match(filename):
				shutil.move(dirpath+filename, dst)
				print("Extracted file %s under %s" % filename, dirpath)

# to generate the table for names and their duration
def extract_timetable(src='temp', dst_file='timetable.txt', pattern='.*\.8K', extract_all=True):
	global AS
	# TODO: to use SWIG
	# get the length of the duration according to its size
	cal_duration = lambda size: (size-AS['header'])*8/(AS['samplerate']*AS['bitrate']*AS['channel'])
	
	timetable = {}
	if extract_all:
		for dirpath, dirnames, filenames in os.walk(src):
			for filename in filenames:
				timetable[filename] = cal_duration((os.stat(dirpath+filename).st_size))
	else:
		prog = re.compile(pattern, re.UNICODE)
		for dirpath, dirnames, filenames in os.walk(src):
			for filename in filenames:
				if prog.match(filename):
					timetable[filename] = cal_duration((os.stat(dirpath+filename).st_size))
	
	if dst_file:
		ordered_timelist = sorted(timetable.items())
		with open(dst_file, 'w') as f:
			for item in ordered_timelist:
				f.write('{0[0]}\t{0[1]}'.format(item))
	return timetable

def extract_text():
	pass

# merged_items is a list of list composed of 2 elements, 
# which is a key and its attributes's list respectively
# such as merged_items=[(key1, [attr1, attr2, ..., attrk]), ...]
def stringify(merged_items, column_indexs=None):
	if column_indexs:
		# item = (key1, [attr1, attr2, ...])
		for item in merged_items:
			attrs = item[1]
			for col in column_indexs:
				attrs[col] = str(attrs[col])
	return merged_items
	


# merge multi files and dicts with a same attribute
# usually, the attribute is the filename at the first column
# TODO: which columns to generate is according to the parameter 'settings'
# such as settings = {'file1': (2, 4), 'dict1': (2, ), ...}
def merge(*files_or_dicts, dst_file='index.txt', settings=None):
	# all components to merge
	merge_components = []
	# loads files into dicts
	for field in files_or_dicts:
		if type(field) is dict:
			merge_components.append(field)
		else:
			trans = {}
			with open(e, 'r') as fd:
				for line in fd:
					columns = line.split()
					if len(columns) > 1:
						trans[columns[0]] = columns[1:]
			merge_components.append(trans)
	# merge
	merge_head = merge_components.pop(0)
	for k, v in merge_head.items():
		for components in merge_components:
			v.append(components[k])
	
	# TODO: to extract a general output function
	# output
	if dst_file:
		ordered_mergence = sorted(merge_head.items())
		# tyr a sample
		try:
			attributes = ordered_mergence[0][1]	
			if len(attributes) > 1:
				'\t'.join(attributes)
		except TypeError, e:
			to_stringify = []
			for i, a in enumerate(attributes):
				if type(a) is not str or unicode:
					to_stringify.append(i)

		ordered_mergence = stringify(ordered_mergence, to_stringify)
		with open(dst_file, 'w') as f:
			for item in merged_items:
				f.write(item[0]+'\t'+'\t'.join(item[1])+'\n')

	return merge_head

if __name__ == '__main__':
	fetch_files(sys.argv[1])
	timetable = extract_timetable()
	merge(timetable, sys.argv[2])

