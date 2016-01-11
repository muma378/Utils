# -*- coding: utf-8 -*-

import os
import re
import sys
import json
from textgrid_generator import output_textgrids

# text follows the key word becomes meaningful
START_KEYWORD = 'item [2]:'	
# the header for item holds 5 lines (intervals: size is included)
ITEM_HEADER_LENGTH = 6
# every interval holds 4 lines
INTERVAL_LENGTH = 4
LONGEST_MUTE = 30
SUFFIX = '.textgrid'

def readfiles(root_dir):
	items = {}
	for dirpath, dirnames, filenames in os.walk(root_dir):
		for filename in filenames:
			if filename.endswith(SUFFIX):
				items[filename.replace(SUFFIX, '')] = parse(dirpath+os.sep+filename)	# already sorted
	return items

# reverse convert lines in the textgrid into a dict with keys described below
# items = { 
# 	'20150810_225453': [
# 		{ 'slice': 52, 'xmin': 193.63785, 'xmax': 195.07, 'text': u'我有去问我一个'},
# 		{ ... }
# 		] 
# 	}
def parse(filename):
	with open(filename, 'r') as f:
		text = f.read()
	clean_list = text.replace('\t', '').split('\n')
	start = clean_list.index(START_KEYWORD) + ITEM_HEADER_LENGTH
	end = len(clean_list)
	shift = 0
	intervals = []
	interval_parser = re.compile('intervals \[(?P<slice>\d+)\]:xmin = (?P<xmin>.*)xmax = (?P<xmax>.*)text = \"(?P<text>.*)\"', re.UNICODE)
	# TODO: add try/except for an interval with more than 4 lines
	# which means \n is contained in the text
	for i in xrange(start, end, INTERVAL_LENGTH):
		try:
			i += shift
			str_interval = ''.join(clean_list[i:i+INTERVAL_LENGTH])
			r = interval_parser.match(str_interval)
			intervals.append({'slice':int(r.group('slice')), 'xmin':float(r.group('xmin')), 'xmax':float(r.group('xmax')), 'text':r.group('text')})
			# in case of the interval is not regular
			# error occured before the line, therefore inter_len is able to increase 
		except AttributeError, IndexError:
			if i < end-INTERVAL_LENGTH: # not enough, read ends 
				# i -= inter_len
				# inter_len += 1
				increment = 0
				while(not r):
					print("Warning: %s at line %d is longer than %d lines, please check" % (filename, i, INTERVAL_LENGTH+increment))
					increment += 1 
					str_interval = ''.join(clean_list[i:i+INTERVAL_LENGTH+increment])
					r = interval_parser.match(str_interval)
				shift += increment
				intervals.append({'slice':int(r.group('slice')), 'xmin':float(r.group('xmin')), 'xmax':float(r.group('xmax')), 'text':r.group('text')})

	return intervals

# truncate the interval without text but logner 30s
# meanwhile generates a json to discribe which file and when was truncated
def truncate(textgrid_dict):
	truncated_dict = {}
	for filename, intervals in textgrid_dict.items():
		shift = 0
		truncated = []
		for i in intervals:
			# no text but too long
			if not i['text'] and i['xmax'] - i['xmin'] > LONGEST_MUTE:
				temp_xmax = i['xmin'] + LONGEST_MUTE
				truncated.append({temp_xmax: i['xmax']})
				i['xmin'] -= shift 
				shift += i['xmax'] - temp_xmax
				i['xmax'] = i['xmin'] + LONGEST_MUTE 	# shifted
			else:
				i['xmin'] -= shift 
				i['xmax'] -= shift
		truncated_dict[filename] = truncated
	return truncated_dict


def output_dict(truncated_dict, dst_file='truncate.json'):
	with open(dst_file, 'w') as f:
		f.write(json.dumps(truncated_dict))

if __name__ == '__main__':
	items = readfiles(sys.argv[1])
	truncated_dict = truncate(items)
	output_textgrids('truncated', items, False)
	output_dict(truncated_dict)
