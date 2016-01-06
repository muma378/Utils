# generate_8k_index.py - usage: 
# it is for integrating all tools to generate the index file
# the index file describes the audio names and their respective info such as duration and subtitle
# Now it implements 3 steps: 
# 1. fetch_files - moves all audio with a specified appendix to a target folder
# 2. extract_timetable - accesses the audio and calculates its duration then writes to a file
# 3. merge - merges files built before and generates an index, its fields can be specified
#-*- coding:utf-8 -*-
import os
import sys
import re
import time
import collections
import shutil
from subprocess import Popen, call
from operator import itemgetter

# following settings shall be understood and written correctly
# audio settings
AS = {
	'header' : 44,
	'samplerate': 8000,
	'bitrate': 16,
	'channel': 1
}

# to indicate which files to merge
# config the setting to specify how to convert names and which fields to use
MERGE_SETTING = (
	('none', 'all'),
	# ('8k2mp3', 'last'),
)

# keys such as mp3index are defined by users, without relation to the real name
FIELDS = {
	'last': -1, 	# only extracts the last field of the file map3index 
	'all': slice(0, None)	# extracts all
}

# map to convert audio names when merging different files
# abc.8K -> abc.mp3
KEY_MAP = {
	# converts the name with '.8K' in src file to .mp3 when mergeing src and mp3index
	'8k2mp3': ('.8K', '.mp3',),
	'none': ('', ''),	# the same
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
			reply = raw_input("Unable to find %s, do you want to create a directory named it? [Y/N]" % arg).lower()
			if reply is "n" or reply is "no":
				exit_prompt("You choosed no, exit now ...")
			else:
				call(mkdir+' '+arg, shell=True)
				# Popen([mkdir, arg], shell=True)
				print("Directory %s is created." % arg)

# actually, tables are dicts. However, generally speaking, the first column from 
# the table composes the key and the rest part compose the value. therefore, 
# the value is a list mostly.
def write_table(table, filename, template=""):
	if filename:
		sorted_table = sorted(table.items())
		with open(filename, 'w') as f:
			if template:
				for item in sorted_table:
					f.write(template.format(item))	# unicode?
			else:
				for item in sorted_table:
					f.write(item[0]+'\t'+concatenate(item[1], '\t')+'\n')
			

# files matched pattern in the path rooted src are fetched and moved to the dst
def fetch_files(src, dst='temp', pattern='.*\.8K'):
	separater = '\\' if os.name is 'nt' else '/'
	validate(src, dst)
	prog = re.compile(pattern, re.UNICODE)
	for dirpath, dirnames, filenames in os.walk(src):
		for filename in filenames:
			if prog.match(filename):
				# TODO:move or copy?
				shutil.copy(dirpath+separater+filename, dst)
				print("Extracted file %s under %s" % (filename, dirpath))


# to generate the table for names and their duration
def extract_timetable(src='temp', dst_file='', pattern='.*\.8K', extract_all=True):
	separater = '\\' if os.name is 'nt' else '/'
	global AS
	# TODO: to use SWIG
	# get the length of the duration according to its size
	cal_duration = lambda size: (size-AS['header'])*8.0/(AS['samplerate']*AS['bitrate']*AS['channel'])
	
	# import pdb;pdb.set_trace()
	timetable = {}
	if extract_all:
		for dirpath, dirnames, filenames in os.walk(src):
			for filename in filenames:
				timetable[filename] = cal_duration((os.stat(dirpath+separater+filename).st_size))
	else:
		prog = re.compile(pattern, re.UNICODE)
		for dirpath, dirnames, filenames in os.walk(src):
			for filename in filenames:
				if prog.match(filename):
					timetable[filename] = cal_duration((os.stat(dirpath+separater+filename).st_size))
	
	# if dst_file:
	# 	ordered_timelist = sorted(timetable.items())
	# 	with open(dst_file, 'w') as f:
	# 		for item in ordered_timelist:
	# 			f.write('{0[0]}\t{0[1]}\n'.format(item))
	write_table(timetable, dst_file, '{0[0]}\t{0[1]}\n')
	return timetable


# transform files to dicts and appends them to the list
def translate(components, files_or_dicts):
	for field in files_or_dicts:
		# if it already is a dict
		if type(field) is dict:
			components.append(field)
		else:
			# if not, loads the file into a dict
			trans = {}
			with open(field, 'r') as fd:
				for line in fd:
					columns = line.split('\t')
					if len(columns) > 1:	# not only with filename
						# assume the first column is the same
						trans[columns[0]] = columns[1:]
			components.append(trans)
	return components


# ABANDONED
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


def concatenate(nested_list, sep='\t'):
	line = ''
	for field in nested_list:
		if type(field) is str or type(field) is unicode:
			line += field.strip()+sep
		elif type(field) is list or type(field) is tuple:
			line += concatenate(field, sep)
		else:
			line += str(field).strip()+sep
	return line.strip()


# match the audio and its subtitles (gcb)
# subtitles are saved in the subtitle_dir, named as GXXX.gcp
# contents in the GXXX.gcp are like: SXXXX\t abcdefg
# respectively, files in the audio_dir named as T0109G0001S0001.8K
def extract_subtitle(audio_dir='temp', subtitle_dir='gcp', audio_suffix='.8K', subtitle_suffix='.gcp', dst_file=''):
	audio_files = os.listdir(audio_dir)
	# match_string = concatenate(audio_files, '\t')
	# import pdb;pdb.set_trace()
	slice_pattern = re.compile('.*(?P<slice>G.*S.*)\\'+audio_suffix)
	try:
		audioname_dict = {slice_pattern.match(af).group('slice'):af for af in audio_files}
	except AttributeError, e:
		pass

	# look up all files under the subtitle dir
	subtitle_dict = {}
	for subtitle_name in os.listdir(subtitle_dir):
		group_name = subtitle_name.replace(subtitle_suffix, '')	# remove suffixes
		subtitle_abspath = os.path.join(subtitle_dir, subtitle_name)
		
		with open(subtitle_abspath, 'r') as fd:
			for line in fd:
				fields = line.split('\t')	# field[0] as part-name, field[1] as subtitle
				try:
					# to find the corresponding fullname
					# pattern = '\t?(?:.*G0001S0001)\.8K'
					# pattern = '\t?(?:.*'+clean_name+fields[0]+')\\'+audio_suffix
					# identifier = re.search(pattern, match_string).group(0)
					subtitle_dict[audioname_dict[group_name+fields[0]]] = fields[1].strip()
				# except AttributeError, e:
				# 	print "Unable to match the pattern " + pattern
				except KeyError, e:
					print "Warning: unable to find the file "+group_name+fields[0]+audio_suffix
	# if dst_file:
	# 	ordered_timelist = sorted(timetable.items())
	# 	with open(dst_file, 'w') as f:
	# 		for item in ordered_timelist:
	# 			f.write('{0[0]}\t{0[1]}\n'.format(item))
	write_table(subtitle_dict, dst_file, '{0[0]}\t{0[1]}\n')
	return subtitle_dict


# merge multi files and dicts with a same attribute
# usually, the attribute is the filename at the first column
# which columns to be generated is specified by the parameter 'settings'
# such as settings = {'file1': (2, 4), 'dict1': (2, ), ...}
# kwargs include dst_file='index.txt', settings=None
def merge(*files_or_dicts, **kwargs):
	# all components to merge
	merge_components = []
	translate(merge_components, files_or_dicts)

	mapped = lambda d, x, i: d[x.replace(KEY_MAP[i][0], KEY_MAP[i][1])]
	
	# TODO: users can define own settings and are able to choose columns automatically 
	# should not specify names by users
	if 'settings' in kwargs.keys():	
		filtered = lambda l, k: itemgetter(kwargs['settings'][k])(l)
	else:
		filtered = lambda l, k: itemgetter(FIELDS[k])(l)
		# filtered = lambda l, k: l

	# merge
	# uses the first dict to lookup key names
	merge_head = merge_components.pop(0)
	for k, v in merge_head.items():
		MS_INDEX = -1
		for components in merge_components:
			MS_INDEX += 1
			try:
				cols = filtered(mapped(components, k, MERGE_SETTING[MS_INDEX][0]), MERGE_SETTING[MS_INDEX][1])
			except KeyError, e:  # no corresponding key in other files
				cols = ''
			try:
				v.append(cols)
			except AttributeError, e:  # v is not a list
				merge_head[k] = [v, cols]

	# TODO: to extract a general output function
	# output
	if 'dst_file' in kwargs.keys():
		dst_file = kwargs['dst_file']
		write_table(merge_head, dst_file)
		# merged_items = sorted(merge_head.items())
		# # try a sample
		# # try:
		# # 	import pdb;pdb.set_trace()
		# # 	attributes = merged_items[1]	
		# # 	if len(attributes) > 1:
		# # 		'\t'.join(attributes)
		# # except TypeError, e:
		# # 	to_stringify = []
		# # 	for i, a in enumerate(attributes):
		# # 		if type(a) is not str or unicode:
		# # 			to_stringify.append(i)

		# # merged_items = stringify(merged_items, to_stringify)
		# with open(dst_file, 'w') as f:
		# 	for item in merged_items:
		# 		f.write(item[0]+'\t'+concatenate(item[1], '\t')+'\n')

	return merge_head
	
if __name__ == '__main__':
	# fetch_files(sys.argv[1])
	# timetable = extract_timetable(dst_file='timetable.txt')
	# subtitle_table = extract_subtitle(dst_file='subtitle.txt')
	# timetable_file = r"C:\Users\xiaoyang\Desktop\ENV_8K\timetable.txt"
	# index_file = r"C:\Users\xiaoyang\Desktop\ENV_8K\533index.txt"
	merge('timetable.txt', 'subtitle.txt', dst_file='index.txt')
