# -*- coding: utf-8 -*-
import os
import re
import sys
from sets import Set
import subprocess
import distance
from parse_blocks import TextgridBlocksParser
from temp_truncate import split_layers
from collect import collect


START_FILE_INDEX = 1
DST_DIR_NAME = 'Astro Awani Buletin Awani New WAV2_'
CMD_TEMPLATE = ('cut.exe' if sys.platform=='win32' else './cut') + ' "{src_file}" "{dst_file}" {start} {end}'
NEWNAME_TEMPLATE = DST_DIR_NAME+"{file_index}_{date}_{time}_{clip_index}_{gender}"
DATETIME_PATTERN = ".*#(?P<date>[0-9x]{8})#(?P<time>[PAM0-9x]{6}).*\.(mp4|wav|TextGrid)$"
datetime_parser = re.compile(DATETIME_PATTERN)

WAV_SUFFIX = '.wav'
TXT_SUFFIX = '.txt'

# collect all marks wrapped with [ & ]
MARKS_SET = Set()
FIND_MARKS = lambda x: re.findall("\[.+?\]", x)

# find all phrase with continual upper letters
UPPER_CASE_PATTERN = re.compile("([A-Z]{2,})([^a-z])", re.UNICODE)
UPPER_CASE_FD = open('upper_case.txt', 'a')

# Find all phrase ended with [other], space inside is allowed
INCLUDE_OTHER_PATTERN = re.compile(".*\[other\]\s*$")
INCLUDE_OTHER_FD = open('other_list.txt', 'a')

def sep_upper_words(match_obj):
	if match_obj.group(1):
		return " " + " ".join(match_obj.group(1)) + " " + match_obj.group(2)
	else:
		return match_obj.group(0)


SUBSTITUTE_RULES = (
	(re.compile("{([^\[}]+?)\]", re.UNICODE), "[\g<1>]"),	# replace [}, {] with []
	(re.compile("\[([^{\]]+?)}", re.UNICODE), "[\g<1>]"),	
	(re.compile("^1"), ""),		# remove the begining marker 1 
	(re.compile("\"\""), "\""),		# replace "" with "
	(re.compile("\"\""), "\" \""),
	(re.compile("([^?])\?([^?])"), "\g<1>??\g<2>"),	# replace ? with ?? but not ?? -> ????
	(re.compile("(\S)\["), "\g<1> ["),	# add space before and after []
	(re.compile("\](\S)"), "] \g<1>"),
	# (re.compile("(?=.)\ (?=\[)", re.UNICODE), ""),	# remove the former space between words and []
	(re.compile("\[(grb|noise|brt)\]", re.UNICODE), "[#\g<1>]"),  # replace [noice] with [#noise]
	# (re.compile("([A-Z ]{2,})([^a-z])"), sep_upper_words),	# insert space between continual upper words
	(re.compile("\s+"), " ")
	)

UNQUALIFIED_RULES = (
	# re.compile("^[^1].+"),	# starts with 1
	re.compile("^\[other\]$"), # only other was included
	re.compile(".*\[other\].+"), # if [other] is existed but not at the end of line
	)
UNQUALIFIED_FD = open('unqualified.txt', 'a')


def find_interval_pair(major, minor):
	index = 0	# index in minor, cause intervals in minor may be composed by serveral parts in major
	error = 0.1  # there may be error in a range
	interval_pairs = []
	minor_interval = minor[index]
	for interval in major:
		while True:
			if interval['xmax'] <= minor_interval['xmax']+error and interval['xmin'] >= minor_interval['xmin']-error:
				if minor_interval['text']:
					interval_pairs.append((interval, minor_interval['text']))	# append the gender info to the speech
				break
			else:
				index += 1
				minor_interval = minor[index]
	return interval_pairs


def split_wav(new_name, audio_file, dst_dir, interval):
	dst_file = os.path.join(dst_dir, new_name+WAV_SUFFIX)
	split_cmd = CMD_TEMPLATE.format(src_file=audio_file, dst_file=dst_file, start=interval['xmin'], end=interval['xmax'])	

	# print split_cmd
	subprocess.check_call(split_cmd, shell=True)

	# args = ['./cut', audio_file, dst_file, str(interval['xmin']), str(interval['xmax'])]
	# subprocess.check_call(args)


def split_textgrid(new_name, dst_dir, interval):
	dst_file = os.path.join(dst_dir, new_name+TXT_SUFFIX)
	text = interval['text'].strip()

	if slots.get(text):
		raise ValueError

	for parser in UNQUALIFIED_RULES:
		if parser.match(text):
			UNQUALIFIED_FD.write(dst_file + ': ' + text + '\n')
			# print text
			raise ValueError

	for parser, repl in SUBSTITUTE_RULES:
		text = parser.sub(repl, text)

	for mark in FIND_MARKS(text):
		MARKS_SET.add(mark)

	if INCLUDE_OTHER_PATTERN.match(text):
		INCLUDE_OTHER_FD.write(dst_file + ': ' + text + '\n')

	# if UPPER_CASE_PATTERN.search(text):
	# 	UPPER_CASE_FD.write(dst_file + ': ' + text + '\n')
	with open(dst_file, 'w') as f:
		f.write(text)
	#f = open("dst_file", "w")
	#f.write(text)
	#f.close()

def clean_gender(gender):
	if gender == 'M' or gender == 'F':
		return gender
	elif re.match("\[([FM])\]", gender):
		return	re.sub("\[([FM])\]", "\g<1>", gender, flags=re.UNICODE)
	else:
		raise ValueError


def split(interval_pairs, audio_file, file_index, original_name, dst_dir=DST_DIR_NAME):
	try:
		datetime_info = get_datetime(original_name)
	except AttributeError as e:
		print ("unable to get info of date and time from the name: " + original_name)
		# datetime_info = {'date': '20xxxxxx', 'time': 'AMxxxx'}
		return

	clip_index = 1
	for interval_pair in interval_pairs:
		try:
			info = {'file_index': file_index, 'date': datetime_info['date'], 'time': datetime_info['time'], 'clip_index': clip_index, 'gender': clean_gender(interval_pair[1])}
		except ValueError as e:
			print ("unable to extract a clean name for gender in " + audio_file + "with index " + str(clip_index))
			continue
		name = NEWNAME_TEMPLATE.format(**info)
		
		try:
			split_textgrid(name, dst_dir, interval_pair[0])
		except ValueError as e:
			print ("unqualified textgrid in " + audio_file)
			continue
		print(name)
		split_wav(name, audio_file, dst_dir, interval_pair[0])
		clip_index += 1
		

def get_datetime(original_name):
	result = datetime_parser.match(original_name)
	return result.groupdict()


def split_pair(root_dir, file_index, pair):
	try:
		# info of generating date and time are contained in the original_name
		audiofile, textfile, original_name = pair
	except ValueError as e:
		import pdb;pdb.set_trace()

	text_file = os.path.join(root_dir, textfile)

	tp.read(text_file, quiet=True)
	intervals = tp.parse_blocks()
	items = split_layers(intervals)
	if not items[1]:
		print ("unable to get any intervals in items[1] of" + textfile)
		raise IOError()
	else:
		interval_pairs = find_interval_pair(items[0], items[1])

	audio_file = os.path.join(root_dir, audiofile)
	print(	)
	split(interval_pairs, audio_file, file_index, original_name)

def find_pairs(*lists):
	pairs = []
	cache_file = DST_DIR_NAME.lower().replace(' ', '_') + '_cache.txt'
	print(cache_file)
	if os.path.exists(cache_file):
		with open(cache_file, 'r') as f:
			cache = f.read().splitlines()
		for line in cache:
			pair = filter(lambda x: x.strip(),  line.split('***'))
			if pair:	# to avoid empty list
				pairs.append(pair)
	else:
		with open(cache_file, 'w') as f:
			for prime in lists[0]:
				pair = [ prime ]
				for minors in lists[1:]:
					similarty = map(lambda minor: distance.nlevenshtein(prime, minor, method=2), minors)
					most_matched = lambda l: minors[ l.index( min(l) ) ]
					candidate = most_matched(similarty)
					pair.append(candidate)
				pairs.append(pair)

				f.write('***'.join(pair))
				f.write(os.linesep)
	return pairs


def get_candidate_lists(root_dir, list_txt, pat1='.wav', pat2='.textgrid'):
	audio_files = filter(lambda x: x.lower().endswith(pat1), os.listdir(root_dir))
	textgrid_files = filter(lambda x: x.lower().endswith(pat2), os.listdir(root_dir))
	BOM = '\xef\xbb\xbf'
	with open(list_txt, 'r') as f:
		raw_content = f.read()
		if raw_content.startswith(BOM):	# utf-8 BOM
			raw_content.replace(BOM, '')
		info_lists = raw_content.splitlines()
	return (audio_files, textgrid_files, info_lists)


if __name__ == '__main__':
	tp = TextgridBlocksParser()
	root_dir = sys.argv[1] #Z:\7. 卜辉\马来语\第四批\BACKUP\马来语第三次数据-Free Malaysia Today-05-03 Z:\7_卜辉\马来语
	list_txt = sys.argv[2] #503.txt
	used_dir3 = sys.argv[3]	# a text file to list direcotories containg all phrases owned 
	
	slots = collect(used_dir3)
	lists = get_candidate_lists(root_dir, list_txt)
	pairs = find_pairs(*lists)
	counter = START_FILE_INDEX
	for pair in pairs:
		try:
			split_pair(root_dir, counter, pair)
		except IOError as e:
			print ("IO error withddd " + pair[1])
		else:
			counter += 1
	print(MARKS_SET)
