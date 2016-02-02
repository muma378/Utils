# -*- coding: utf-8 -*-
# qualify_textgrid.py - usage: 
# to validate the format of a textgrid
# author: Xiao Yang <xiaoyang0117@gmail.com>
# date: 2016.02.02
import os
import sys
import re
import codecs
from traverse import traverse

PATTERNS = (
	(re.compile('^\s*intervals \[(?P<slice>\d+)\]:'), 'slice', int),
	(re.compile('^\s*xmin = (?P<xmin>[\d\.]+)'), 'xmin', float),
	(re.compile('^\s*xmax = (?P<xmax>[\d\.]+)'), 'xmax', float),
	(re.compile('^\s*text = "(?P<text>.*)"'), 'text', str),
	# for a special case that a text has multiple lines
	(re.compile('^\s*text = "(?P<text>.*)'), 'text', str),
	(re.compile('^(?P<text>.*)"'), 'text', str),
)

RULES_PATTERNS = (
	(re.compile('^([0-2])?(?(1)(?P<text>.+)|$)', re.UNICODE), lambda x: x.group('text') , u'错误：第{lineno}行不是以数字开始或只包含数字，文本内容为“{text}”'),
	(re.compile('^(\D+)'), lambda x: re.sub('\[[SNTP]\]', '', x.group(0), re.IGNORECASE), u'错误：第{lineno}行文本中包含数字，文本内容为“{text}”'),
	(re.compile('((?!\[\w\]).)*$', re.UNICODE), lambda x: x.group(0), u'错误：第{lineno}行噪音符号标识错误，包含非SNTP字符，文本内容为"{text}"'),
	(re.compile('(.{3,})$', re.UNICODE), lambda x: True, u'错误：第{lineno}行文本长度小于3，文本内容为"{text}"'),
)
	
TEXT_KEY = 'text'

MEANINGLESS_CHAR = '\x00'

CODINGS = (
	('utf-8-sig', (codecs.BOM_UTF8,)),
	('utf-16', (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)),
	('utf-32', (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)),
	)

def code_det(headline, default='utf-8'):
	for enc,boms in CODINGS:
		if any(headline.startswith(bom) for bom in boms): return enc
	return default

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

		# try to match row by row, which is pattern by pattern
		for line in lines:
			lineno += 1;
			p = PATTERNS[pat_idx]
			
			r = p[0].match(line)
			if r:
				interval[p[1]] = p[2](r.group(p[1]))
				pat_idx += 1

			# in case of multi-lines exised in a pair of doubule quotes
			elif APPEND_STATUS:
				if PATTERNS[pat_idx+2][0].match(line):
					p = PATTERNS[pat_idx+2]
					interval[p[1]] += p[2](p[0].match(line).group(p[1]))
					pat_idx += 1
					APPEND_STATUS = False
				else:
					interval[p[1]] += line
			elif pat_idx == 3 and PATTERNS[pat_idx+1][0].match(line):
				p = PATTERNS[pat_idx+1]
				interval[p[1]] = p[2](p[0].match(line).group(p[1]))
				APPEND_STATUS = True
			
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
	intervals = reverse_parse(src_file)
	validate(intervals)
	
def main():
	file_or_dir = sys.argv[1]
	if os.path.isfile(file_or_dir): 
		traverse(file_or_dir, '', qualify, target='.textgrid')
	else:
		qualify(file_or_dir, '')
	

if __name__ == '__main__':
	main()