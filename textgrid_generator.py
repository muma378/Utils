# -*- coding: utf-8 -*-

# TextGridGenerator.py - usage: python TextGridGenerator.py configure.txt
# to parse the configure.txt and translate it into textgrid files
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2015.12.28
# the format of the text to parse is below:
# http://crowdfile.blob.core.chinacloudapi.cn/cutted-wav-blob/20150810_225453_52_193.63_194.975.wav	1	0.00785	1.44	我有去问我一个	1.44

import os
import sys
import re
import subprocess


APPENDIX = ".TextGrid"
TEMPLATE_HEADER = """File type = "ooTextFile"
Object class = "TextGrid"

xmin = {global_xmin}
xmax = {global_xmax}
tiers? <exists>
size = 2
item []:
"""

TEMPLATE_ITEM = """	item [{item_index}]:
		class = "IntervalTier"
		name = "text"
		xmin = {global_xmin}
		xmax = {global_xmax}
		intervals: size = {intervals_size}
"""

TEMPLATE_INTERVALS = """			intervals [{interval_index}]:
			xmin = {local_xmin}
			xmax = {local_xmax}
			text = "{text}"
"""

URL_PATTERN = '.*/(?P<name>.+)_(?P<slice>\d+)_(?P<start>[\d.]+)_(?P<end>[\d.]+)\.wav'
# URL_PATTERN = '^(?P<name>.+)_(?P<slice>\d+)_(?P<start>[\d.]+)_(?P<end>[\d.]+)\.mp3'

#sort and organize
def parse_file(src, items):
	with open(src, "r") as f:
		for line in f:
			parse_line(line, items)

# to convert lines in the config into a dict with keys described below
# items = { 
# 	'20150810_225453': [
# 		{ 'slice': 52, 'xmin': 193.63785, 'xmax': 195.07, 'text': u'我有去问我一个'},
# 		{ ... }
# 		] 
# 	}
def parse_line(line, items):
	columns = line.split('\t')
	if columns[1] == '1':
		url = unicode(columns[0], 'utf-8')
		try:
			groups = re.search(URL_PATTERN, url, re.UNICODE).groupdict()
			info = {'slice': int(groups['slice']), 'xmin': str(float(groups['start'])+float(columns[2])), 'xmax': str(float(groups['start'])+float(columns[3])), 'text': columns[4]}
		except (AttributeError, ValueError) as e:
			if columns[2] == 'None':
				columns[2] = 0
				info = {'slice': int(groups['slice']), 'xmin': str(float(groups['start'])+float(columns[2])), 'xmax': str(float(groups['start'])+float(columns[3])), 'text': columns[4]}
			else:
				print "Unable to parse the url: " + url

		else:
			try:
				items[groups['name']].append(info)
			except KeyError, e:
				items[groups['name']] = [info]

def generate_interval(aslice, interval_index, text=''):
	return TEMPLATE_INTERVALS.format(interval_index=interval_index, local_xmin=aslice['xmin'], local_xmax=aslice['xmax'], text=text)

def generate_output(filled_slices):
	intervals_size = len(filled_slices)
	global_xmin = filled_slices[0]['xmin']
	global_xmax = filled_slices[intervals_size-1]['xmax']
	
	output = TEMPLATE_HEADER.format(**locals())
	# first time: fill it with empty text
	item_index = 1
	output += TEMPLATE_ITEM.format(**locals())
	for i, aslice in enumerate(filled_slices, start=1):
		output += generate_interval(aslice, i)

	# second time: fill it with real text
	item_index = 2
	output += TEMPLATE_ITEM.format(**locals())
	for i, aslice in enumerate(filled_slices, start=1):
		output += generate_interval(aslice, i, text=aslice['text'])
	return output

# to fill 'gaps' in the list of slices
# gaps means the values of xmax and xmin in continus slices are not the same
def prefill_items(slices):
	ordered_slices = sorted(slices, key=lambda x:x['slice'])
	previous_xmax = 0
	filled_slices = []
	for aslice in ordered_slices:
		if previous_xmax != aslice['xmin']:
			filled_slices.append({'slice': aslice['slice']-1, 'xmin': previous_xmax, 'xmax': aslice['xmin'], 'text': ''})
		filled_slices.append(aslice)
		previous_xmax = aslice['xmax']
	return filled_slices

def output_textgrids(root_dir, items, prefill=True):
	mkdir = 'MD' if os.name is 'nt' else 'mkdir'
	sep = '\\' if os.name is 'nt' else '/'
	if not os.path.exists(root_dir):
		subprocess.check_call(mkdir+' '+root_dir, shell=True)
	# ordered = collections.OrderedDict(sorted(items.items()))
	for filename, slices in items.items():
		dst = root_dir + sep + filename + '.textgrid'
		with open(dst, "w") as f:
			if prefill:
				slices =prefill_items(slices)
			f.write(generate_output(slices))


if __name__ == '__main__':
	items = {}
	parse_file(sys.argv[1], items)
	directory_name = sys.argv[1].split('.')[0]
	output_textgrids(directory_name, items)