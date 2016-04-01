# -*- coding: utf-8 -*-
import os
import re
import sys
import subprocess
import distance
from parse_blocks import TextgridBlocksParser
from temp_truncate import split_layers

CMD_TEMPLATE = ('cut.exe' if sys.platform=='win32' else './cut') + ' "{src_file}" "{dst_file}" {start} {end}'
NEWNAME_TEMPLATE = "Astro{file_index}_{date}_{time}_{clip_index}_{sex}"
DATETIME_PATTERN = ".*#(?P<date>[0-9x]{8})#(?P<time>[PAM0-9x]{6}).*\.mp4$"
datetime_parser = re.compile(DATETIME_PATTERN)

WAV_SUFFIX = '.wav'
TXT_SUFFIX = '.txt'


SUBSTITUTE_RULES = (
	(re.compile("\[(.+?)[})]", re.UNICODE), "[\g<1>]"),	# replace [} to []
	(re.compile("(?=.)\ (?=\[)", re.UNICODE), ""),	# remove space between words and []
	(re.compile("\[(grb|noise|brt)\]", re.UNICODE), "[#\g<1>]"),  # replace [noice] to [#noise]
	)

UNQUALIFIED_RULE = re.compile(".*\[other\].+") # if [other] is existed but not at the end


def find_interval_pair(major, minor):
	index = 0	# index in minor, cause intervals in minor may be composed by serveral parts in major
	error = 0.1  # there may be error in a range
	interval_pairs = []
	minor_interval = minor[index]
	for interval in major:
		while True:
			# if minor_interval['xmax'] <= interval['xmin'] + error:
			# 	index += 1
			# 	minor_interval = minor[index]
			if interval['xmax'] <= minor_interval['xmax']+error and interval['xmin'] >= minor_interval['xmin']-error:
				if minor_interval['text']:
					interval_pairs.append((interval, minor_interval['text']))
				break
			else:
				index += 1
				minor_interval = minor[index]
	return interval_pairs


def split_wav(new_name, audio_file, dst_dir, interval):
	dst_file = os.path.join(dst_dir, new_name+WAV_SUFFIX)
	split_cmd = CMD_TEMPLATE.format(src_file=audio_file, dst_file=dst_file, start=interval['xmin'], end=interval['xmax'])	

	# print split_cmd
	# subprocess.check_call(cmd, shell=True)

	# args = ['./cut', audio_file, dst_file, str(interval['xmin']), str(interval['xmax'])]
	# subprocess.check_call(args)


def split_textgrid(new_name, dst_dir, interval):
	dst_file = os.path.join(dst_dir, new_name+TXT_SUFFIX)
	text = interval['text'].strip()

	if UNQUALIFIED_RULE.match(text):
		print dst_file

	# import pdb;pdb.set_trace()
	for parser, repl in SUBSTITUTE_RULES:
		text = parser.sub(repl, text)

	with open(dst_file, 'w') as f:
		f.write(text)


def split(interval_pairs, audio_file, file_index, original_name, dst_dir="backup/"):
	try:
		datetime_info = get_datetime(original_name)
	except AttributeError, e:
		print "unable to get info of date and time from the name: " + original_name
		# datetime_info = {'date': '20xxxxxx', 'time': 'AMxxxx'}
		return

	for clip_index, interval_pair in enumerate(interval_pairs, start=1):
		info = {'file_index': file_index, 'date': datetime_info['date'], 'time': datetime_info['time'], 'clip_index': clip_index, 'sex': interval_pair[1]}
		name = NEWNAME_TEMPLATE.format(**info)
		
		split_wav(name, audio_file, dst_dir, interval_pair[0])
		split_textgrid(name, dst_dir, interval_pair[0])
		

def get_datetime(original_name):
	result = datetime_parser.match(original_name)
	return result.groupdict()


def split_pair(root_dir, file_index, pair):
	try:
		# info of generating date and time are contained in the original_name
		audiofile, textfile, original_name = pair
	except ValueError, e:
		import pdb;pdb.set_trace()

	text_file = os.path.join(root_dir, textfile)
	tp.read(text_file, quiet=True)
	intervals = tp.parse_blocks()
	items = split_layers(intervals)
	interval_pairs = find_interval_pair(items[0], items[1])

	audio_file = os.path.join(root_dir, audiofile)
	split(interval_pairs, audio_file, file_index, original_name)

def find_pairs(*lists):
	pairs = []
	
	cache_file = 'cache.txt'
	if os.path.exists(cache_file):
		with open(cache_file, 'r') as f:
			cache = f.read().splitlines()
		for line in cache:
			pairs.append(filter(lambda x: x.strip(), map(lambda x: x.strip("' \""), line.split('***'))))
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
	root_dir = sys.argv[1]
	list_txt = sys.argv[2]

 	lists = get_candidate_lists(root_dir, list_txt)
	pairs = find_pairs(*lists)

	for i, pair in enumerate(pairs, start=1):
		split_pair(root_dir, i, pair)

