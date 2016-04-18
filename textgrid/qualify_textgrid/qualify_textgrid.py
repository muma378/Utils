# -*- coding: utf-8 -*-
# qualify_textgrid.py - usage: python qualify_textgrid src_file[src_root] [timeit]
# to validate the format of a textgrid
# or to calculate the sum time of text in respectively categories
# author: Xiao Yang <xiaoyang0117@gmail.com>
# date: 2016.02.16
import os
import sys
import re

from parse_blocks import TextgridBlocksParser as TextgridParser
from censor import RulesCensor
from calculagraph import Calculagraph, CategoricalCalculagraph



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