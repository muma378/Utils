# TextGridGenerator.py - usage: python TextGridGenerator.py configure.txt
# to parse the configure.txt and translate it into textgrid files
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2015.12.28

import os
import sys
import re
import subprocess

import collections

APPENDIX = ".TextGrid"
TEMPLATE_HEADER = """File type = "ooTextFile"
Object class = "TextGrid"
"""

TEMPLATE_ITEM = """
xmin = {global_xmin}
xmax = {global_xmax}
tiers? <exists>
size = 1
item []:
	item [1]:
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

#sort and organize
def parse_file(src, items):
	with open(src, "r") as f:
		for line in f:
			parse_line(line, items)



def parse_line(line, items):
	columns = line.split('\t')
	if columns[1] == '1':
		url = unicode(columns[0], 'utf-8')
		try:
			groups = re.search('.*/(?P<name>.+)_(?P<slice>\d+)_(?P<start>[\d.]+)_(?P<end>[\d.]+)\.wav', url, re.UNICODE).groupdict()
		except AttributeError, e:
			print "Can not parse the url: " + url
		else:
			info = {'slice': int(groups['slice']), 'xmin': str(float(groups['start'])+float(columns[2])), 'xmax': str(float(groups['start'])+float(columns[3])), 'text': columns[4]}
			try:
				items[groups['name']].append(info)
			except KeyError, e:
				items[groups['name']] = [info]
		

if __name__ == '__main__':
	items = {}
	parse_file(sys.argv[1], items)
	directory_name = sys.argv[1].split('.')[0]
	subprocess.call('mkdir '+directory_name, shell=True)
	ordered = collections.OrderedDict(sorted(items.items()))
	for k, v in ordered.iteritems():
		dst = directory_name + '/' + k + '.textgrid'
		with open(dst, "w") as f:
			f.write(TEMPLATE_HEADER)
			v = sorted(v, key=lambda x:x['slice'])
			intervals_size = len(v)
			head = TEMPLATE_ITEM.format(global_xmin=v[0]['xmin'], global_xmax=v[intervals_size-1]['xmax'], intervals_size=intervals_size)
			body = head
			for i, s in enumerate(v):
				body += TEMPLATE_INTERVALS.format(interval_index=i, local_xmin=s['xmin'], local_xmax=s['xmax'], text=s['text'])
			f.write(body)

