# -*- coding: utf-8 -*-
import os
import re
import unittest
from calculagraph import Calculagraph, CategoricalCalculagraph


class CalculagraphTestCase(unittest.TestCase):
	def setUp(self):
		self.intervals = [{"text":"1测试", "xmin":0.0, "xmax":2.0, "lineno":1},
						  {"text":"", "xmin":2.0, "xmax":2.5, "lineno":2},
						  {"text":"2测试", "xmin":2.5, "xmax":30.5, "lineno":3},
						  {"text":"1", "xmin":4.5, "xmax":3.5, "lineno":4},
						  ]

		MATCH_PARSER = re.compile('.+', re.UNICODE)
		self.cg = Calculagraph(MATCH_PARSER)

	def test_measure(self):
		duration = self.cg.measure(self.intervals)
		self.assertEqual(duration, 30.0)
		self.assertEqual(len(self.cg.errors), 1)

	def test_prints(self):
		self.cg.measure(self.intervals)
		output = self.cg.output_duration()	# 's'
		self.assertEqual(len(output), 1)
		self.assertEqual(output[0], u"有效时长为30.000000秒")

		output = self.cg.output_duration('m')
		self.assertEqual(len(output), 1)
		self.assertEqual(output[0], u"有效时长为0.500000分")


	def test_get_unit_display(self):
		divider, unit_display = self.cg.get_unit_display('h')
		self.assertEqual(divider, 3600.0)	
		self.assertEqual(unit_display, u'小时')

		with self.assertRaises(KeyError) as ke:
			self.cg.get_unit_display('k')



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
		self.cg = CategoricalCalculagraph(TEXT_CATEGORY_PARSER, TEXT_CATEGORY_KEY, MARKS_MEANING)

	def test_measure(self):
		durations = self.cg.measure(self.intervals)
		self.assertEqual(durations['1'], 4)
		self.assertEqual(durations['2'], 0.5)
		self.assertEqual(len(self.cg.errors), 1)

	def test_prints(self):
		self.cg.measure(self.intervals)
		output = self.cg.output_duration()
		self.assertEqual(len(output), 2)
		self.assertEqual(output[0], u"1-时长为4.000000秒")