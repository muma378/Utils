# -*- coding: utf-8 -*-
# qualify_textgrid.py - usage: python qualify_textgrid src_file[src_root] [timeit]
# to validate the format of a textgrid
# or to calculate the sum time of text in respectively categories
# author: Xiao Yang <xiaoyang0117@gmail.com>
# date: 2016.02.16
import os
import sys
import re
import codecs
from itertools import cycle

import chardet

RULES_PATTERNS = (
	(re.compile('^([0-2])?(?(1)(?P<text>.+)|$)', re.UNICODE), lambda x: x.group('text') , u'错误1：第{lineno}行不是以特定数字开始或只包含数字，文本内容为“{text}”'),
	(re.compile('^(\D+)$'), lambda x: re.sub('\[[SNTPsntp]\]', '', x.group(0)), u'错误2：第{lineno}行除文本开始处外另包含数字，文本内容为“{text}”'),
	(re.compile('((?!\[\w\]).)*$', re.UNICODE), lambda x: x.group(0), u'错误3：第{lineno}行噪音符号标识错误，包含非SNTP字符，文本内容为"{text}"'),
	(re.compile(u'((?![【】]).)*$', re.UNICODE), lambda x: x.group(0), u'错误4：第{lineno}行包含全角括号，文本内容为"{text}"'),
	(re.compile('(.{3,25})$', re.UNICODE), lambda x: True, u'错误5：第{lineno}行文本长度小于3或大于25，文本内容为"{text}"'),
)
TEXT_KEY = 'text'

TEXT_CATEGORY_PARSER = re.compile('^(?P<category>[0-2])\D.*', flags=re.UNICODE)

MARKS_MEANING = {
	'1': u'1-近端',
	'2': u'2-远端',
	'0': u'0-其他人说话',
}


logger = None
time_logger = None

def setup(target):
	global logger
	global time_logger
	if os.path.isdir(target):
		if target.endswith('\\'):
			target = target[:-1]
		logfile = os.path.join(target, os.path.basename(target)+'.log')
		timelog = os.path.join(target, 'duration.log')
	elif os.path.isfile(target):
		logfile = target + '.log'
		timelog = target + '_duration.log'
	logger = open(logfile, 'w')
	time_logger = open(timelog, 'w')

def teardown():
	logger.close()
	time_logger.close()

def loginfo(msg, stdout=False, timelog=False):
	if stdout:
		print(msg)
	logger.write((msg+os.linesep).encode('utf-8'))
	if timelog:
		logtime(msg)	#syntax sugar

def logtime(msg, stdout=False):
	if stdout:
		print(msg)
	time_logger.write((msg+os.linesep).encode('utf-8'))


class CycleIterator(object):
	""" a wrapper for the itertools.cycle """
	def __init__(self, iterable):
		super(CycleIterator, self).__init__()
		self.iterable = iterable
		self.iterator = cycle(iterable)
		self.value = None
	
	def head(self):
		return self.iterable[0]

	def tail(self):
		return self.iterable[-1]

	def next(self):
		self.value = self.iterator.next()
		return self.value

	def end(self):
		return self.value == self.tail()

	# to loop from the begining
	def reset(self):
		self.iterator = cycle(self.iterable)

	def index(self, i):
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
		(re.compile('^(?P<text>.*)"\s*$'), 'text', str),
	)

	PATTERN_KEYS = ('pattern', 'key', 'type')

	def __init__(self, coding='utf-8'):
		super(TextgridParser, self).__init__()
		self.default_coding = coding
		self.intervals = []

	def reset(self):
		self.intervals = []

	def read(self, filename):
		self.filename = filename
		with open(filename, 'rb') as f:
			content = f.read()
			# self.coding = self.code_det(content[0:10])
			self.coding = chardet.detect(content)['encoding']
			try:
				self.lines = content.decode(self.coding).encode(self.default_coding).splitlines()
			except UnicodeError, e:
				loginfo(u'>>文件：{filename}'.format(filename=self.filename), stdout=True)
				loginfo(u'解码时发生错误，请选择合适的文本编辑器，并以utf-8编码格式保存后，再运行此程序', stdout=True)
				loginfo('')
				raise IOError

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

	def update(self, interval, item_pattern, line, append_mode=False):
		ip = item_pattern
		if append_mode:
			# only for text
			interval[ip['key']] += ip['type'](ip['pattern'].match(line).group(ip['key']))
		else:
			interval.update({ ip['key']: ip['type'](ip['pattern'].match(line).group(ip['key'])) }) 
		return interval

	def match(self, item_pattern, line):
		return item_pattern['pattern'].match(line)

	def append(self, interval):
		pass

	def parse(self):
		print(u'正在解析{filename}...'.format(filename=self.filename))
		loginfo(u'>>文件：{filename}'.format(filename=self.filename), timelog=True)
		
		lineno = 0
		interval = {}
		APPEND_MODE = False
		self.reset()
		bp_iter = CycleIterator(self.pack(TextgridParser.PATTERN_KEYS, TextgridParser.BLOCK_PATTERNS))
		mp_iter = CycleIterator(self.pack(TextgridParser.PATTERN_KEYS, TextgridParser.MULTILINES_PATTERN))

		block_begining = bp_iter.head()
		item_pattern = bp_iter.next()
		for line in self.lines:
			lineno += 1

			# reset the block parsing once the line matched the begining pattern
			if self.match(block_begining, line):
				# self.update(interval, block_begining, line)
				# not the start actually, exception occured in parsing last block
				if item_pattern != block_begining:
					loginfo(u'错误：无法解析第%d行，不是textgrid标准格式，已跳过' % (lineno-1), stdout=True)	# last line instead of the current
					interval = {}
					APPEND_MODE = False
					bp_iter.reset()
					item_pattern = bp_iter.next()
					
			# when a text existed in multiple lines
			elif APPEND_MODE:
				# import pdb;pdb.set_trace()
				if self.match(mp_iter.tail(), line): # match the pattern of end line
					self.update(interval, mp_iter.tail(), line, APPEND_MODE)
					interval['lineno'] = lineno
					self.intervals.append(interval)	# block ends
					interval = {}
					item_pattern = bp_iter.next()	# loop to the begining
					APPEND_MODE = False
					# 2. block ending
				else:
					# append the middle part of the text
					self.update(interval, mp_iter.index(1), line, APPEND_MODE) 
			
			# match the item in sequence
			if self.match(item_pattern, line):
				self.update(interval, item_pattern, line)

				# if the end of the block was matched
				if bp_iter.end():
					interval['lineno'] = lineno
					self.intervals.append(interval)
					interval = {}

				# loop to the begining
				item_pattern = bp_iter.next()
				# 1. block ending

			#　match the begining of multi-lines text instead of a single line
			elif self.match(mp_iter.head(), line):
				self.update(interval, mp_iter.head(), line)
				APPEND_MODE = True


def validate(intervals, quiet=False):
	validated = []
	error_no = 0
	if not quiet:
		print(u'正在验证...')
	for interval in intervals:
		legal = True 	# to append legal textgrid to the list
		text = interval[TEXT_KEY].decode('utf-8')
		if text:
			for rp,fn,msg in RULES_PATTERNS:
				result = rp.match(text)
				if result:
					text = fn(result)
				else:
					if not quiet:
						loginfo(msg.format(lineno=interval['lineno'], text=interval['text'].decode('utf-8')))
					legal = False
					error_no += 1
					break
		else:
			legal = False
		if legal:
			validated.append(interval)
	if not quiet:
		print(u'验证完成，检测到%d个错误' % error_no)
		if error_no == 0:
			loginfo(u'Succeed')
		else:
			loginfo(u'共%d个错误被检测到' % error_no)
	loginfo('')	# extra space line
	return validated


def timeit(intervals):
	assoeted_intervals = {}
	for interval in intervals:
		try:
			# assume it was validated before
			category = TEXT_CATEGORY_PARSER.match(interval[TEXT_KEY].decode('utf-8')).group('category')
			time_len = interval['xmax'] - interval['xmin']
			if time_len < 0:
				logtime(u'错误: 在第%d行检测到xmax的值大于xmin值' % interval['lineno'])
				
			assoeted_intervals[category] += time_len
		except KeyError, e:
			assoeted_intervals[category] = time_len
		except AttributeError, e:
			print('error: did not validate the textgrid before calculating the time')	# for debugging
			sys.exit(0)
	print_duration(assoeted_intervals)
	return assoeted_intervals

SUM_DURATION = {}
def timestat(assoeted_duration):
	for key, val in assoeted_duration.items():
		try:
			SUM_DURATION[key] += val
		except KeyError, e:
			SUM_DURATION[key] = val

TIME_UNIT = {
	's':(1, u'秒'),
	'm':(60.0, u'分'),
	'h':(3600.0, u'小时')
}

def print_duration(assoeted_duration, unit='s'):
	try:
		divider, unit_display = TIME_UNIT[unit]
	except KeyError, e:
		print('error: unkown choice for unit')	#for debugging
		sys.exit(1)
	try:
		for key, val in assoeted_duration.items():
			logtime(u'%s总时长为 %f%s' % (MARKS_MEANING[key], val/divider, unit_display), stdout=True)
	except KeyError, e:
		print('error: unsupported marks included')
	logtime('')	# extra line spaces for ending of files


def qualify(src_file, _):
	tp.read(src_file)
	tp.parse()
	validated = validate(tp.intervals)
	durations = timeit(validated)
	timestat(durations)

def traverse(src_dir, dst_dir, fn, target='.txt'):
	for dirpath, dirnames, filenames in os.walk(src_dir):
		for filename in filenames:
			if filename.endswith(target):
				try:
					src_file = os.path.join(dirpath, filename)
					src_dir_len = len(src_dir) if src_dir.endswith(os.sep) else len(src_dir)+1
					dst_file = os.path.join(dst_dir, src_file[src_dir_len:])	# should not use replace
					fn(src_file, dst_file)
				except Exception as e:
					pass

def main():
	file_or_dir = sys.argv[1]
	setup(file_or_dir)
	file_or_dir = unicode(file_or_dir, 'gb2312')

	if os.path.isdir(file_or_dir): 
		traverse(file_or_dir, '', qualify, target=('.textgrid', '.TextGrid'))
		logtime(u'>>文件夹%s 内统计的总时长为' % file_or_dir, stdout=True)
		print_duration(SUM_DURATION, unit='s')
	elif os.path.isfile(file_or_dir):
		qualify(file_or_dir, '')
	else:
		print(u"指定的文件或目录不存在")
	
	teardown()

 
if __name__ == '__main__':
	tp = TextgridParser()
	main()