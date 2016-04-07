# -*- coding: utf-8 -*-
import os
import re
import unittest
from evaluate import Calculagraph

class CalculagraphTestCase(unittest.TestCase):
	def setUp(self):
		self.intervals = [{"text":"1测试", "xmin":0.0, "xmax":2.0, "lineno":1},
						  {"text":"2测试", "xmin":2.0, "xmax":2.5, "lineno":2},
						  {"text":"1测试", "xmin":2.5, "xmax":4.5, "lineno":3},
						  {"text":"2测试", "xmin":4.5, "xmax":3.5, "lineno":4},
						  ]
		self.cg = Calculagraph()

	def test_measure(self):
		durations = self.cg.measure(self.intervals)
		self.assertEqual(durations['1'], 4)
		self.assertEqual(durations['2'], 0.5)
		self.assertEqual(len(self.cg.errors), 1)

	def test_prints(self):
		pass