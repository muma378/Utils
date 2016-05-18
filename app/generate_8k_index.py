#!/usr/local/bin/python
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
import shutil
import argparse
import subprocess
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

# command to truncate wavs
CMD_TRUNCATE = 'truncate.exe {src} {dst}'

# TODO: to print the error traceback
def exit_prompt(msg):
	print msg
	time.sleep(2)
	sys.exit(0)


def validate(*args):
	for arg in args:
		if not os.path.exists(arg):
			reply = raw_input("Unable to find %s, do you want to create a directory named it? [Y/N]" % arg).lower()
			if reply is "n" or reply is "no":
				exit_prompt("You choosed no, exit now ...")
			else:
				os.makedirs(arg)
				print("Directory %s is created." % arg)

# actually, tables are dicts. However, generally speaking, the first column from 
# the table composes the key and the rest part compose the value. therefore, 
# the value is a list mostly.
def write_table(table, filename, template=""):
	if filename:`
		sorted_table = sorted(table.items())
		with open(filename, 'w') as f:
			if template:
				for item in sorted_table:
					f.write(template.format(item))	# unicode?
			else:
				for item in sorted_table:
					f.write(item[0]+'\t'+concatenate(item[1], '\t')+'\n')

			
# files matched pattern in the path rooted src are fetched and moved to the dst
def fetch_folders(src, dst='temp', refer='refer.txt', pattern=''):
	validate(src, refer, dst)
	with open(refer, 'r') as f:
		candidates = f.read().split()
	unextracted = { c:1 for c in candidates }

	# unsupported right now
	# prog = re.compile(pattern, re.UNICODE)

	for dirpath, dirnames, filenames in os.walk(src):
		for dirname in dirnames:
			# TODO: a more reasonable way to decide whether move
			if unextracted.get(dirname):
				print("Extracting folder %s to %s" % (dirname, dst))
				try:
					shutil.copytree(os.path.join(dirpath, dirname), os.path.join(dst, dirname))
					unextracted[dirname] = 0
				except OSError, e:
					print("File exists: %s" %  os.path.join(dst, dirname))
	
	for c in candidates:
		if unextracted[c]:
			print("Warning: unable to extract %s" % c)


# files matched pattern in the path rooted src are fetched and moved to the dst
def fetch_files(src, dst='temp', pattern='.*\.8K'):
	validate(src, dst)
	prog = re.compile(pattern, re.UNICODE)
	for dirpath, dirnames, filenames in os.walk(src):
		for filename in filenames:
			if prog.match(filename):
				# TODO:move or copy?
				shutil.copy(os.path.join(dirpath, filename), dst)
				print("Extracted file %s under %s" % (filename, dirpath))


# to generate the table for names and their duration
def extract_timetable(src='temp', dst_file='', pattern='.*\.8K', extract_all=True):
	global AS
	# TODO: to use SWIG
	# get the length of the duration according to its size
	cal_duration = lambda size: (size-AS['header'])*8.0/(AS['samplerate']*AS['bitrate']*AS['channel'])
	
	timetable = {}
	if extract_all:
		for dirpath, dirnames, filenames in os.walk(src):
			for filename in filenames:
				timetable[filename] = cal_duration(os.stat(os.path.join(dirpath, filename)).st_size)
	else:
		prog = re.compile(pattern, re.UNICODE)
		for dirpath, dirnames, filenames in os.walk(src):
			for filename in filenames:
				if prog.match(filename):
					timetable[filename] = cal_duration(os.stat(os.path.join(dirpath, filename)).st_size)
	
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


# match the audio and its subtitles (gcp)
# subtitles are saved in the subtitle_dir, named as GXXX.gcp
# contents in the GXXX.gcp are like: SXXXX\t subtitle
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
	write_table(subtitle_dict, dst_file, '{0[0]}\t{0[1]}\n')
	return subtitle_dict


# merge multi files and dicts with a same attribute
# usually, the attribute is the filename at the first column
# which columns to be generated is specified by the parameter 'filter_settings'
# such as filter_settings = {'file1': (2, 4), 'dict1': (2, ), ...}
# kwargs include dst_file='index.txt', filter_settings=None
def merge(*files_or_dicts, **kwargs):
	# all components to merge
	merge_components = []
	translate(merge_components, files_or_dicts)

	mapped = lambda d, x, i: d[x.replace(KEY_MAP[i][0], KEY_MAP[i][1])]
	
	# TODO: users can define own settings and are able to choose columns automatically 
	# should not specify names by users
	# if 'filter_settings' in kwargs.keys():
	# 	filtered = lambda l, k: itemgetter(*kwargs['filter_settings'][k])(l)
	# else:
	# 	filtered = lambda l, k: itemgetter(FIELDS[k])(l)
	
	def filtered(table, setting_name):
		try:
			settings = kwargs['filter_settings'][k]
		except KeyError, e:
			settings = FIELDS.get(k)

		if settings is None:
			return table
		# multi continuous fields, such as slice(2, None)
		elif type(settings) is slice:
			return itemgetter(settings)(table)
		# multi isolated fields, such as [2, 5, 6]
		elif type(settings) is list or type(settings) is tuple:
			return itemgetter(*settings)(table)
		# only one field, such as -1
		elif type(settings) is int:
			return table[settings]
		# incorrect settings
		else:
			exit_prompt("Error: Uninterpretable settings: " + str(settings))

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

	if 'dst_file' in kwargs.keys():
		dst_file = kwargs['dst_file']
		write_table(merge_head, dst_file)

	return merge_head

# TODO: add following functions
# fetch_folders('first_edition', 'refer.txt', 'test')
def call_function(util, args):
	if util == "fetch":
		if args.type == 'file':
			fetch_files(args.src, args.dst, args.pattern)
		else:	# args.type == 'folder'
			fetch_folders(args.src, args.dst, args.refer, args.pattern)
	elif util == "timetable":
		extract_timetable(args.src, args.file, args.pattern, False)
	elif util == "subtitle":
		extract_subtitle(args.audio[0], args.text[0], args.audio[1], args.text[1], args.file)
	elif util == "merge":
		merge(args.files, dst_file=args.file)
	# TODO: create a subcommand to execute all process
	elif util == "all":	
		pass
	


def main():
	parser = argparse.ArgumentParser(prog=sys.argv[0], description='Integrated tools for generating available audio and index.')

	# create the interface to sub-command
	subparser = parser.add_subparsers(title='subprocesses', description='call an isolated process')
	# fetch_files
	fetch_parser = subparser.add_parser('fetch', help='copy or move files matched the parttern under src to dst')
	fetch_parser.add_argument('-t', '--type', default='file', choices=('file', 'folder'), help='move files or folders')
	fetch_parser.add_argument('-s', '--src', required=True, help='source directory to extract')
	fetch_parser.add_argument('-d', '--dst', default='temp', help='destination directory to put')
	fetch_parser.add_argument('-p', '--pattern', default='.*\.8K', help='regular expression to match')
	fetch_parser.add_argument('-r', '--refer', default='refer.txt', help='text to specify which folders to move, only needed when --type is folder')
	# extract_timetable
	timetable_parser = subparser.add_parser('timetable', help='extract audio to generate a table containing names and duration')
	timetable_parser.add_argument('-s', '--src', required=True, help='source directory to scan audio')
	timetable_parser.add_argument('-f', '--file', default='timetable.txt', help='destination file to save tables')
	timetable_parser.add_argument('-p', '--pattern', default='.*\.8K', help='file to extract shall match the pattern')
	# extract_subtitle
	subtitle_parser = subparser.add_parser('subtitle', help='extract text from gcp to match the audio')
	subtitle_parser.add_argument('-a', '--audio', required=True, nargs=2, default=('temp', '.8K'), metavar=('audio_dir', 'audio_suffix'),
		help='audio directory and suffix')
	subtitle_parser.add_argument('-t', '--text', required=True, nargs=2, default=('gcp', '.gcp'), metavar=('subtitle_dir', 'subtitle_suffix'),
		help='subtitle directory and suffix')
	subtitle_parser.add_argument('-f', '--file', default='subtitle.txt', help='destination file to save tables')
	# merge
	merge_parser = subparser.add_parser('merge', help='merge several index files')
	merge_parser.add_argument('files', nargs='*', help='files to merge, noted the first columns must be the same')
	merge_parser.add_argument('-f', '--file', default='index.txt', help='destination file to save data')

	args = parser.parse_args(sys.argv[1:])
	call_function(sys.argv[1], args)


if __name__ == '__main__':
	main()
	# fetch_files(sys.argv[1])
	# timetable = extract_timetable(dst_file='timetable.txt')
	# subtitle_table = extract_subtitle(dst_file='subtitle_table.txt')
	# timetable_file = r"C:\Users\xiaoyang\Desktop\ENV_8K\timetable.txt"
	# index_file = r"C:\Users\xiaoyang\Desktop\ENV_8K\533index.txt"
	# merge(timetable, subtitle_table, dst_file='index.txt')
	