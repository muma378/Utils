# -*- coding: utf-8 -*-
import os
import re
import unittest
import StringIO
import calculagraph

class BaseCalculagraphTestCase(unittest.TestCase):
	def setUp(self):
		self.cg = calculagraph.BaseCalculagraph()	

	def test_get_unit_display(self):
		divider, unit_display = self.cg.get_unit_display('h')
		self.assertEqual(divider, 3600.0)	
		self.assertEqual(unit_display, u'小时')

		with self.assertRaises(KeyError) as ke:
			self.cg.get_unit_display('k')

	def test_output(self):
		output = StringIO.StringIO()
		self.cg.output(output, 10)
		self.assertEqual(output.getvalue(), u"10秒"+os.linesep)

		output = StringIO.StringIO()
		self.cg.output(output, 3600, msg=u"{extra_arg}测试{duration_display}{unit_display}", unit='h', extra_arg=u"输出")
		self.assertEqual(output.getvalue(), u"输出测试1.0小时")

class PatternCalculagraphTestCase(unittest.TestCase):
	def setUp(self):
		self.intervals = [{"text":"1测试", "xmin":0.0, "xmax":2.0, "lineno":1},
						  {"text":"", "xmin":2.0, "xmax":2.5, "lineno":2},
						  {"text":"2测试", "xmin":2.5, "xmax":30.5, "lineno":3},
						  {"text":"1", "xmin":4.5, "xmax":3.5, "lineno":4},
						  ]

		MATCH_PARSER = re.compile('.+', re.UNICODE)
		self.cg = calculagraph.PatternCalculagraph(MATCH_PARSER)

	def test_measure(self):
		cg = self.cg.measure(self.intervals)
		self.assertEqual(cg.duration, 30.0)
		self.assertEqual(len(cg.errors), 1)
		self.assertEqual(cg.errors[0], u'错误: 在第4行检测到xmax的值大于xmin值')

	def test_output_duration(self):
		self.cg.measure(self.intervals)
		
		output = StringIO.StringIO()
		self.cg.output_duration(output)	# 's'
		self.assertEqual(output.getvalue(), u"文件有效时长为30.0秒"+os.linesep)

		output = StringIO.StringIO()
		self.cg.output_duration(output, 'm')
		self.assertEqual(output.getvalue(), u"文件有效时长为0.5分"+os.linesep)


class CategoricalCalculagraphTestCase(unittest.TestCase):
	def setUp(self):
		self.intervals = [{"text":"1测试", "xmin":0.0, "xmax":2.0, "lineno":1},
						  {"text":"2测试", "xmin":2.0, "xmax":2.5, "lineno":2},
						  {"text":"1测试", "xmin":2.5, "xmax":4.5, "lineno":3},
						  {"text":"2测试", "xmin":4.5, "xmax":3.5, "lineno":4},
						  ]

		TEXT_CATEGORY_PARSER = re.compile('^(?P<category>[1-4])\D.*', flags=re.UNICODE)
		TEXT_CATEGORY_KEY = 'category'

		MARKS_MEANING = {
			'1': '1-',
			'2': '2-',
			'3': '3-',
			'4': '4-'
		}
		self.cg = calculagraph.CategoricalCalculagraph(TEXT_CATEGORY_PARSER, TEXT_CATEGORY_KEY, MARKS_MEANING)

	def test_measure(self):
		cg = self.cg.measure(self.intervals)
		self.assertEqual(cg.duration['1'], 4)
		self.assertEqual(cg.duration['2'], 0.5)
		self.assertEqual(len(cg.errors), 1)

	def test_output_duration(self):
		self.cg.measure(self.intervals)
		
		output = StringIO.StringIO()
		self.cg.output_duration(output)
		print_durations = filter(lambda x: x.strip(), output.getvalue().split(os.linesep))
		self.assertEqual(len(print_durations), 2)
		self.assertEqual(output.getvalue(), u"1-时长为4.0秒"+os.linesep+u"2-时长为0.5秒"+os.linesep)


class OverallCalculagraphTestCase(unittest.TestCase):
	def setUp(self):
		self.intervals1 = [{"text":"1测试", "xmin":0.0, "xmax":2.0, "lineno":1},
						  {"text":"", "xmin":2.0, "xmax":2.5, "lineno":2},
						  {"text":"2测试", "xmin":2.5, "xmax":30.5, "lineno":3},
						  {"text":"1", "xmin":4.5, "xmax":3.5, "lineno":4},
						  ]

		self.intervals2 = [{"text":"1测试", "xmin":0.0, "xmax":2.0, "lineno":1},
						  {"text":"", "xmin":2.0, "xmax":3, "lineno":2},
						  {"text":"3测试", "xmin":3, "xmax":30.5, "lineno":3},
						  {"text":"测试", "xmin":30.5, "xmax":31, "lineno":4},

						  ]

	def test_dict_add(self):
		d1 = {'a':1, 'b':2}
		d2 = {'a':3, 'c':4}
		self.assertEqual(calculagraph.dict_add(d1, d2), {'a':4, 'b':2, 'c':4})

	def test_init_with_patterncal(self):
		pcg = calculagraph.PatternCalculagraph(re.compile('.+', re.UNICODE))
		self.ocg = calculagraph.OverallCalculagraph(pcg)
		self.assertEqual(self.ocg.accum, 0)
		self.ocg.measure(self.intervals1)
		self.assertEqual(self.ocg.accum, 30)	# 2+28
		self.ocg.measure(self.intervals2)
		self.assertEqual(self.ocg.accum, 60)	# 30 + 2+27.5+0.5
		output = StringIO.StringIO()
		self.ocg.output_duration(output, unit='m')
		self.assertEqual(output.getvalue(), u"文件夹内统计的总时长为:"+os.linesep+u"文件有效时长为1.0分"+os.linesep)

		pcg = calculagraph.PatternCalculagraph()
		self.ocg = calculagraph.OverallCalculagraph(pcg)
		self.assertEqual(self.ocg.accum, 0)
		self.ocg.measure(self.intervals1)
		self.assertEqual(self.ocg.accum, 30.5)	# 2+0.5+28
		self.ocg.measure(self.intervals2)
		self.assertEqual(self.ocg.accum, 61.5)	# 30.5 + 2+1+27.5+0.5
		self.ocg.accum = 5400
		output = StringIO.StringIO()
		self.ocg.output_duration(output)
		self.assertEqual(output.getvalue(), u"文件夹内统计的总时长为:"+os.linesep+u"文件有效时长为1.5小时"+os.linesep)

	def test_init_with_catcal(self):
		TEXT_CATEGORY_PARSER = re.compile('^(?P<category>[1-4])\D.*', flags=re.UNICODE)
		TEXT_CATEGORY_KEY = 'category'

		MARKS_MEANING = {
			'1': '1-',
			'2': '2-',
			'3': '3-',
			'4': '4-'
		}
		ccg = calculagraph.CategoricalCalculagraph(TEXT_CATEGORY_PARSER, TEXT_CATEGORY_KEY, MARKS_MEANING)
		self.ocg = calculagraph.OverallCalculagraph(ccg)
		self.assertEqual(self.ocg.accum, {})
		self.ocg.measure(self.intervals1)
		self.assertEqual(self.ocg.accum['1'], 2)	# 2.0 - 0.0
		self.assertEqual(self.ocg.accum['2'], 28)	# 30.5 - 2.5

		self.ocg.measure(self.intervals2)
		self.assertEqual(self.ocg.accum['1'], 4)	# 2 + 2.0-0.0
		self.assertEqual(self.ocg.accum['2'], 28)	# 28
		self.assertEqual(self.ocg.accum['3'], 27.5)		#30.5 - 3
		output = StringIO.StringIO()
		self.ocg.output_duration(output, unit='s')
		print_durations = filter(lambda x: x.strip(), output.getvalue().split(os.linesep))
		self.assertEqual(print_durations[0], u"文件夹内统计的总时长为:")
		self.assertTrue(u"1-时长为4.0秒" in print_durations)
		self.assertTrue(u"2-时长为28.0秒" in print_durations)
		self.assertTrue(u"3-时长为27.5秒" in print_durations)


