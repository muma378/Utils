# -*- coding: utf-8 -*-
import os
import shutil
import unittest
from mock import patch, PropertyMock
from parse import TextgridParser, BlockIterator


class BlockIteratorTestCase(unittest.TestCase):
	def setUp(self):
		self.block = (
			(('test_start', ), ('test_end', ), ('test_error1', 'test_error2')),
			(re.compile('^xmin = (?P<xmin>[\d\.]+)'), 'xmin', float),
			(re.compile('^xmax = (?P<xmax>[\d\.]+)'), 'xmax', float),
			(re.compile('^tiers\? <exists>'), None, type(None)),
			(re.compile('^size = (?P<size>\d+)'), 'size', int),
			(re.compile('^item \[\]: '), None, type(None)),
			)
		self.bi = BlockIterator(*self.block)

	def test_init_info(self):
		self.assertEqual(self.bi.start[0], 'test_start')
		self.assertEqual(self.bi.end[0], 'test_end')
		self.assertEqual(self.bi.error[0], 'test_error1')
		self.assertEqual(self.bi.error[1], 'test_error2')

	def test_iterable(self):
		for i, item in enumerate(self.bi, start=1):
			self.assertEqual(item, self.block[i])


class TextgridParserTestCase(unittest.TestCase):
	def setUp(self):
		self.tp = TextgridParser()

	def test_feed(self):
		filenames = ('temp1.txt', 'temp2.txt', 'temp3.txt', 'temp4.txt')
		raw_data = ('hello,test', u'测试utf-8', u'测试utf-16-le', u'测试utf-16-be')
		codings = ('ascii', 'utf-8', 'utf-16', 'gb2312')

		def generate_files(filename, raw_data, coding):
			with open(filename, 'w') as f:
				f.write(raw_data.encode(coding))
		
		for i in range(len(raw_data)):
			generate_files(filenames[i], raw_data[i], codings[i])	
			self.tp.feed(filenames[i])
			# self.assertEqual(self.tp.content, raw_data[i].encode('utf-8'))
			os.remove(filenames[i])

	def test_iterable(self):
		pass
