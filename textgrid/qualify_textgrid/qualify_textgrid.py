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

from parse_blocks import TextgridBlocksParser as TextgridParser

RULES_PATTERNS = (
	(re.compile('^([1-4])?(?(1)(?P<text>.+)|$)', re.UNICODE), lambda x: x.group('text') , u'错误1：第{lineno}行不是以特定数字开始或只包含数字，文本内容为“{text}”'),
	(re.compile('^(\D+)$'), lambda x: re.sub('\[[SNTPsntp]\]', '', x.group(0)), u'错误2：第{lineno}行除文本开始处外另包含数字，文本内容为“{text}”'),
	(re.compile('((?!\[\w\]).)*$', re.UNICODE), lambda x: x.group(0), u'错误3：第{lineno}行噪音符号标识错误，包含非SNTP字符，文本内容为"{text}"'),
	(re.compile(u'((?![【】]).)*$', re.UNICODE), lambda x: x.group(0), u'错误4：第{lineno}行包含全角括号，文本内容为"{text}"'),
	(re.compile('(.{3,25})$', re.UNICODE), lambda x: True, u'错误5：第{lineno}行文本长度小于3或大于25，文本内容为"{text}"'),
)
TEXT_KEY = 'text'

TEXT_CATEGORY_PARSER = re.compile('^(?P<category>[1-4])\D.*', flags=re.UNICODE)

MARKS_MEANING = {
	'1': '1-',
	'2': '2-',
	'3': '3-',
	'4': '4-'
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


def timeit(intervals, title=None):
	assoeted_intervals = {}
	for interval in intervals:
		try:
			# assume it was validated before
			category = TEXT_CATEGORY_PARSER.match(interval[TEXT_KEY].decode('utf-8')).group('category')
			time_len = interval['xmax'] - interval['xmin']
			if time_len < 0:
				logtime(u'错误: 在第%d行检测到xmax的值大于xmin值' % interval['lineno'], stdout=True)
			else:
				assoeted_intervals[category] += time_len
		except KeyError, e:
			# import pdb;pdb.set_trace()
			assoeted_intervals[category] = time_len
		except AttributeError, e:
			continue
			# print('error: did not validate the textgrid before calculating the time')	# for debugging
			# sys.exit(0)
	print_duration(assoeted_intervals, title=title)
	return assoeted_intervals

def timestat(assoeted_duration, glob_duration):
	for key, val in assoeted_duration.items():
		try:
			glob_duration[key] += val
		except KeyError, e:
			glob_duration[key] = val

TIME_UNIT = {
	's':(1, u'秒'),
	'm':(60.0, u'分'),
	'h':(3600.0, u'小时')
}

def print_duration(assoeted_duration, unit='s', title=None):
	if title:
		logtime(title)
	try:
		divider, unit_display = TIME_UNIT[unit]
	except KeyError, e:
		print('error: unkown choice for unit')	#for debugging
		sys.exit(1)
	try:
		for key, val in assoeted_duration.items():
			logtime(u'%s时长为 %f%s' % (MARKS_MEANING[key], val/divider, unit_display), stdout=True)
	except KeyError, e:
		print('error: unsupported marks included')
	logtime('')	# extra line spaces for ending of files


SUM_DURATION = {}
VALI_DURATION = {}
def qualify(src_file, _):
	tp.read(src_file)
	tp.parse()
	all_durations = timeit(tp.intervals, title=u'>>各端总时长:')
	validated = validate(tp.intervals)
	validated_durations = timeit(validated, title=u'>>各端有效时长:')
	# TODO: refactor here
	timestat(all_durations, SUM_DURATION)	
	timestat(validated_durations, VALI_DURATION)

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
					print e
					print("Unable to process %s" % src_file)

def main():
	file_or_dir = sys.argv[1]
	setup(file_or_dir)
	file_or_dir = unicode(file_or_dir, 'gb2312')

	if os.path.isdir(file_or_dir): 
		traverse(file_or_dir, '', qualify, target=('.textgrid', '.TextGrid'))
		logtime(u'>>文件夹%s 内统计的总时长为\t 原始数据总时长为%f小时' % (file_or_dir, tp.original_duration_sum/3600.0), stdout=True)
		logtime(u'>>各端总时长:', stdout=True)
		print_duration(SUM_DURATION, unit='h')
		logtime(u'>>各端有效时长:', stdout=True)
		print_duration(VALI_DURATION, unit='h')
	elif os.path.isfile(file_or_dir):
		qualify(file_or_dir, '')
	else:
		print(u"指定的文件或目录不存在")
	
	teardown()

 
if __name__ == '__main__':
	tp = TextgridParser()	# to avoid initializing multiple times
	main()