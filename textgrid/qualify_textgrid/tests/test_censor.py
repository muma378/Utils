# -*- coding: utf-8 -*-
import os
import re
import unittest
from censor import RulesCensor

class RulesCensorTestCase(unittest.TestCase):
	def setUp(self):
		self.RULES = (
			(re.compile('^([1-4])?(?(1)(?P<text>.+)|$)', re.UNICODE), lambda x: x.group('text') , u'错误1：第{lineno}行不是以特定数字开始或只包含数字，文本内容为“{text}”'),
			(re.compile('^(\D+)$', re.UNICODE), lambda x: re.sub('\[[SNTPsntp]\]', '', x.group(0)), u'错误2：第{lineno}行除文本开始处外另包含数字，文本内容为“{text}”'),
			(re.compile('((?!\[\w\]).)*$', re.UNICODE), lambda x: x.group(0), u'错误3：第{lineno}行噪音符号标识错误，包含非SNTP字符，文本内容为"{text}"'),
			(re.compile(u'((?![【】]).)*$', re.UNICODE), lambda x: x.group(0), u'错误4：第{lineno}行包含全角括号，文本内容为"{text}"'),
			(re.compile('(.{3,25})$', re.UNICODE), lambda x: True, u'错误5：第{lineno}行文本长度小于3或大于25，文本内容为"{text}"'),
		)

	def test_first_rule(self):
		parser, fn, msg = self.RULES[0]
		self.assertTrue(parser.match("1测试一"))
		self.assertFalse(parser.match("9测试一"))
		self.assertFalse(parser.match("测试一"))
		self.assertFalse(parser.match("1"))
		self.assertEqual(fn(parser.match("1测试一")), '测试一')

	def test_second_rule(self):
		parser, fn, msg = self.RULES[1]
		self.assertTrue(parser.match("测试二"))
		self.assertFalse(parser.match("测试2"))
		self.assertEqual(fn(parser.match("测试[s]二")), "测试二")
		self.assertEqual(fn(parser.match("测试[m]二")), "测试[m]二")
		self.assertEqual(fn(parser.match("测试二")), "测试二")

	def test_third_rule(self):
		parser, fn, msg = self.RULES[2]
		self.assertTrue(parser.match("测试三"))
		self.assertFalse(parser.match("测试[m]三"))

	def test_forth_rule(self):
		parser, fn, msg = self.RULES[3]
		self.assertTrue(parser.match(u"测[试]四"))
		self.assertFalse(parser.match(u"测【试】四"))
		self.assertFalse(parser.match(u"测【试四"))

	def test_validate(self):
		self.rc = RulesCensor(self.RULES)
		intervals = [{"text":u"1短", "lineno":1}, 
					 {"text":u"错误一", "lineno":2},
					 {"text":u"1合格语[s]句", "lineno":3},
					 ]
		
		qualified = self.rc.validate(intervals)
		self.assertEqual(len(self.rc.errors), 2)
		self.assertEqual(len(qualified), 1)
		self.assertEqual(qualified[0]["lineno"], 3)


