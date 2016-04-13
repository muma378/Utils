# -*- coding: utf-8 -*-

import re
import log

logger = log.LogHandler('qualifier.log', stdout=True)

INTERVAL_KEY_TEXT = 'text'
INTERVAL_KEY_LINENO = 'lineno'
INTERVAL_KEY_XMAX = 'xmax'
INTERVAL_KEY_XMIN = 'xmin'


TEXT_CATEGORY_PARSER = re.compile('^(?P<category>[1-4])\D.*', flags=re.UNICODE)
TEXT_CATEGORY_KEY = 'category'

MARKS_MEANING = {
	'1': '1-',
	'2': '2-',
	'3': '3-',
	'4': '4-'
}

TIME_UNIT = {
	's':(1, u'秒'),
	'm':(60.0, u'分'),
	'h':(3600.0, u'小时')
}

# 3 elements listed in each tuple, the first starnds for the rule of validating
# the second is a function to extract a part (or whole) of the text for next steps
# the third indicates the message displayed when error happened
REGEXP_RULES = (
	(re.compile('^([1-4])?(?(1)(?P<text>.+)|$)', re.UNICODE), lambda x: x.group('text') , u'错误1：第{lineno}行不是以特定数字开始或只包含数字，文本内容为“{text}”'),
	(re.compile('^(\D+)$'), lambda x: re.sub('\[[SNTPsntp]\]', '', x.group(0)), u'错误2：第{lineno}行除文本开始处外另包含数字，文本内容为“{text}”'),
	(re.compile('((?!\[\w\]).)*$', re.UNICODE), lambda x: x.group(0), u'错误3：第{lineno}行噪音符号标识错误，包含非SNTP字符，文本内容为"{text}"'),
	(re.compile(u'((?![【】]).)*$', re.UNICODE), lambda x: x.group(0), u'错误4：第{lineno}行包含全角括号，文本内容为"{text}"'),
	(re.compile('(.{3,25})$', re.UNICODE), lambda x: True, u'错误5：第{lineno}行文本长度小于3或大于25，文本内容为"{text}"'),
)