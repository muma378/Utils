# basenames.py - usage: python basenames.py root_dir
# to extract basenames in the text file which under the root dir
# author: xiaoyang <xiaoyang0117@gmail.com>
# date: 2015.01.13
import os
import sys
import re

# URL_PATTERN = '.*/(?P<name>.+)_(?P<slice>\d+)_(?P<start>[\d.]+)_(?P<end>[\d.]+)\.(?P<format>.+)$'
# URL_PATTERN = '.*/(?P<name>.+)_(?P<slice>\d+)_(?P<start>[\d.]+)_(?P<end>[\d.]+)\.[wav|mp3|8K]'
# URL_PATTERN = '^(?P<name>.+)_(?P<slice>\d+)_(?P<start>[\d.]+)_(?P<end>[\d.]+)\.[mp3|wav]'
# URL_PATTERN = '.*/(?P<name>.+)_(?P<start>[\d.]+)_(?P<end>[\d.]+)\.[wav|mp3|8K]'

PATTERN_BODY = '(?P<name>.+)_(?P<slice>\d+)_(?P<start>[\d.]+)_(?P<end>[\d.]+)\.(?P<format>.+)$'
SLICE_PATTERN = '_(?P<slice>\d+)'

def guess_pattern(line):
	if line.startswith('http:'):
		PATTERN_HEAD = '.*/'
	else:
		PATTERN_HEAD = '^'
	pattern = PATTERN_HEAD + PATTERN_BODY
	try:
		groups = re.match(pattern, line, re.UNICODE).groupdict()
		assert float(groups['slice']) < 10000
		return pattern
	except (AttributeError, AssertionError) as e:
		return pattern.replace(SLICE_PATTERN, '')

def parse_line(line, names):
	columns = line.split('\t')
	if columns[1] == '1':
		url = unicode(columns[0], 'utf-8')
		try:
			pattern = guess_pattern(url)
			groups = re.search(pattern, url, re.UNICODE).groupdict()
			info = {'slice': int(groups['slice']), 'xmin': str(float(groups['start'])+float(columns[2])), 'xmax': str(float(groups['start'])+float(columns[3])), 'text': columns[4]}
		except (AttributeError, ValueError) as e:
			if columns[2] == 'None':
				columns[2] = 0
				info = {'slice': int(groups['slice']), 'xmin': str(float(groups['start'])+float(columns[2])), 'xmax': str(float(groups['start'])+float(columns[3])), 'text': columns[4]}
				print("Warning: the start time for %s is None" % columns[0])
			else:
				print "Unable to parse the url: " + url
				return
		names.append(groups['name']+'.'+groups['format']+'\n')
		# names.append(groups['name']+'.wav\n')	# all original audio are waves


def readfiles(root_dir):
	for file in os.listdir(root_dir):
		if file.endswith('.txt'):
			names = []
			with open(file, 'r') as f:
				for line in f:
					parse_line(line, names)
			with open(file.replace('.txt', 'names.txt'), 'w') as f:
				for name in names:
					f.write(name.encode('utf-8'))

if __name__ == '__main__':
	readfiles(sys.argv[1])
