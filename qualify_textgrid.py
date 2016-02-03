# -*- coding: utf-8 -*-
# qualify_textgrid.py - usage: 
# to validate the format of a textgrid
# author: Xiao Yang <xiaoyang0117@gmail.com>
# date: 2016.02.02
import os
import sys
import re
import codecs
from itertools import cycle
from traverse import traverse


RULES_PATTERNS = (
	(re.compile('^([0-2])?(?(1)(?P<text>.+)|$)', re.UNICODE), lambda x: x.group('text') , u'错误：第{lineno}行不是以数字开始或只包含数字，文本内容为“{text}”'),
	(re.compile('^(\D+)'), lambda x: re.sub('\[[SNTP]\]', '', x.group(0), re.IGNORECASE), u'错误：第{lineno}行文本中包含数字，文本内容为“{text}”'),
	(re.compile('((?!\[\w\]).)*$', re.UNICODE), lambda x: x.group(0), u'错误：第{lineno}行噪音符号标识错误，包含非SNTP字符，文本内容为"{text}"'),
	(re.compile('(.{3,})$', re.UNICODE), lambda x: True, u'错误：第{lineno}行文本长度小于3，文本内容为"{text}"'),
)
	
TEXT_KEY = 'text'

MEANINGLESS_CHAR = '\x00'

class CycleIterator(object):
	""" a wrapper for the itertools.cycle """
	def __init__(self, iterable):
		super(CycleIterator, self).__init__()
		self.iterable = iterable
		self.iterator = cycle(iterable)
	
	def begin():
		return self.iterable[0]

	def last():
		return self.iterable[-1]

	def next():
		self.iterator.next()

	# to loop from the begining
	def reset():
		self.iterator = cycle(self.iterable)

	def index(i):
		return self.iterable[i]


class TextgridParser(object):
	"""translate the textgrid into a dict"""
	CODINGS = (
		('utf-8-sig', (codecs.BOM_UTF8,)),
		('utf-16', (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)),
		('utf-32', (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)),
		)

	BLOCK_PATTERNS = (
		(re.compile('^\s*intervals \[(?P<slice>\d+)\]:'), 'slice', int),
		(re.compile('^\s*xmin = (?P<xmin>[\d\.]+)'), 'xmin', float),
		(re.compile('^\s*xmax = (?P<xmax>[\d\.]+)'), 'xmax', float),
		(re.compile('^\s*text = "(?P<text>.*)"'), 'text', str),
		)
	# for a special case that a text has multiple lines
	MULTILINES_PATTERN = (
		(re.compile('^\s*text = "(?P<text>.*)'), 'text', str),
		(re.compile('^(?P<text>.*)$'), 'text', str),	# to adapt the new line
		(re.compile('^(?P<text>.*)"'), 'text', str),
	)

	PATTERN_KEYS = ('pattern', 'key', 'type')

	def __init__(self, coding='utf-8'):
		super(TextgridParser, self).__init__()
		self.default_coding = coding
		self.intervals = {}

	def read(self, filename):
		with open(filename, 'r') as f:
			content = f.read()
			self.coding = self.code_det(content[0:10])
			self.lines = content.decode(self.coding).encode(self.default_coding).splitlines()

	def code_det(self, headline, default='utf-8'):
		for enc,boms in TextgridParser.CODINGS:
			if any(headline.startswith(bom) for bom in boms): 
				return enc
		return default

	def pack(self, keys, tuples):
		package = []
		for vals in tuples:
			package.append({ keys[i]:vals[i] for i in range(len(keys)) })
		return package

	# def next_pattern(self):
	# 	if self.append_mdoe:
	# 		return 

	def update(interval, item_pattern, line, append_mode=False):
		ip = item_pattern
		if append_mode:
			interval.update({ ip['key']: ip['type'](ip['pattern'].match(line).group(ip['key'])) }) 
		else:
			# only for text
			interval[ip['key']] += ip['type'](ip['pattern'].match(line).group(ip['key']))
		return interval

	def match(item_pattern, line):
		return item_pattern['pattern'].match(line)

	def parse(self):
		lineno = 0
		# interval = {}
		APPEND_MODE = False
		bp_iter = CycleIterator(TextgridParser.BLOCK_PATTERNS)
		mp_iter = CycleIterator(TextgridParser.MULTILINES_PATTERN)

		block_begining = bp_iter.next()
		item_pattern = bp_iter.next()
		for line in self.lines:
			lineno += 1

			if self.match(block_begining, line):
				# reset the block parsing once the line matched the begining pattern
				interval = {}
				# self.update(interval, block_begining, line)
				bp_iter.reset()
			
			elif APPEND_MODE:	# a text existed in multiple lines
				if self.match(mp_iter.last(), line): # match the pattern of end line
					self.update(interval, mp_iter.last(), line, APPEND_MODE)
					self.intervals.append(interval)	# block ends
					APPEND_MODE = False
				else:
					# append the text body
					self.update(interval, mp_iter.index(1), line, APPEND_MODE) 
			
			if self.match(item_pattern, line):
				pass
				


def reverse_parse(textgrid):
	with open(textgrid, 'r') as f:
		content = f.read()
		coding = code_det(content.splitlines()[0])
		lines = content.decode(coding).encode('utf-8').splitlines()

		lineno = 0
		pat_idx = 0
		interval = {}
		intervals = []
		APPEND_STATUS = False

		for line in lines:
			lineno += 1
			p = PATTERNS[pat_idx] 

			if APPEND_STATUS:
				if PATTERNS[pat_idx+2][0].match(line):
					p = PATTERNS[pat_idx+2]
					interval[p[1]] += p[2](p[0].match(line).group(p[1]))
					pat_idx += 1
					APPEND_STATUS = False
				elif PATTERNS[0][0].match(line):	# jump to the begining of a block
					interval[p[1]] = p[2](PATTERNS[0][0].match(line).group(p[1]))
					pat_idx = 1
				else:
					interval[p[1]] += line

			elif p[0].match(line):
				interval[p[1]] = p[2](p[0].match(line).group(p[1]))
				pat_idx += 1
			elif pat_idx == 3 and PATTERNS[pat_idx+1][0].match(line):
				p = PATTERNS[pat_idx+1]
				interval[p[1]] = p[2](p[0].match(line).group(p[1]))
				APPEND_STATUS = True
			elif pat_idx > 0:		#exception catched in parsing
				print(u"解析textgrid过程中发生异常，已跳过第{0}行".format(lineno-1))
				# reset
				interval = {}
				pat_idx = 0
				if PATTERNS[pat_idx][0].match(line):	# jump to the begining of a block
					interval[p[1]] = p[2](PATTERNS[pat_idx][0].match(line).group(p[1]))
					pat_idx += 1
			if pat_idx == 4:
				interval['lineno'] = lineno
				intervals.append(interval)
				interval = {}
				pat_idx = 0

		return intervals

def validate(intervals):
	for interval in intervals:
		text = interval[TEXT_KEY].decode('utf-8')
		# import pdb;pdb.set_trace()
		if text:
			for rp,fn,msg in RULES_PATTERNS:
				result = rp.match(text)
				if result:
					text = fn(result)
				else:
					print(msg.format(lineno=interval['lineno'], text=interval['text'].decode('utf-8')))
					break


def qualify(src_file, _):
	# intervals = reverse_parse(src_file)
	tp = TextgridParser()
	tp.parse()
	validate(tp.intervals)
	
def main():
	file_or_dir = sys.argv[1]
	if os.path.isdir(file_or_dir): 
		traverse(file_or_dir, '', qualify, target='.textgrid')
	elif os.path.isfile(file_or_dir):
		qualify(file_or_dir, '')
	else:
		print(u"指定的文件或目录不存在")
	

if __name__ == '__main__':
	main()