# -*- coding: utf-8 -*-
import os
import re
import shutil
import unittest
from mock import MagicMock
from mock import patch, PropertyMock
from parse_textgrid import BlockIterator, TextgridParser, PatternManager


class BlockIteratorTestCase(unittest.TestCase):
	def setUp(self):
		self.block = (
			(('test_start', ), ('test_end', ), ('test_error1', 'test_error2')),
			PatternManager('^xmin = (?P<xmin>[\d\.]+)', 'xmin', float),
			PatternManager('^xmax = (?P<xmax>[\d\.]+)', 'xmax', float),
			PatternManager('^tiers\? <exists>', None, type(None)),
			PatternManager('^size = (?P<size>\d+)', 'size', int),
			PatternManager('^item \[\]: ', None, type(None)),
			)

		self.mock_tp = MagicMock()
		self.bi = BlockIterator(self.mock_tp, *self.block)

	def test_init_ctrl(self):
		self.assertEqual(self.bi.start[0], 'test_start')
		self.assertEqual(self.bi.end[0], 'test_end')
		self.assertEqual(self.bi.error[0], 'test_error1')
		self.assertEqual(self.bi.error[1], 'test_error2')

	def test_iterable(self):
		for i, pm in enumerate(self.bi, start=1):
			self.assertEqual(pm.key, self.block[i].key)

	def test_match_start(self):
		self.test_block_iter = BlockIterator(
			self.mock_tp, 
			(1, 2, 3), 
			PatternManager('^test(?P<num>\d+)', 'num', int),)
		self.mock_tp.get = MagicMock(return_value=self.test_block_iter)
	
		self.assertEqual(self.bi.match_start('test123'), self.test_block_iter)
		self.assertIsNone(self.bi.match_start('321tset'))

	def test_empty_start(self):
		with patch('parse_textgrid.BlockIterator.start', new_callable=PropertyMock, create=True) as mock_start:
			mock_start.return_value = ()
			self.assertIsNone(self.bi.match_start('test'))

	def test_reset_if_return(self):
		self.test_block_iter = BlockIterator(
			self.mock_tp, 
			(1, 2, 3), 
			PatternManager('^test(?P<num>\d+)', 'num', int),)
		self.mock_tp.get = MagicMock(return_value=self.test_block_iter)
		self.bi.index = 10

		self.bi.match_start('321tset')
		self.assertEqual(self.bi.index, 10)
		self.bi.match_start('test123')
		self.assertEqual(self.bi.index, 0)


class PatternManagerTestCase(unittest.TestCase):
	def setUp(self):
		self.args = ('^test(?P<num>\d+)', 'num', int)
		self.pm = PatternManager(*self.args)

	def test_init(self):
		self.assertEqual(self.pm.parser.pattern, self.args[0])
		self.assertEqual(self.pm.key, self.args[1])

	def test_match(self):
		self.assertEqual(self.pm.match('test123').group(self.args[1]), '123')
		self.assertIsNone(self.pm.match('321tset'))

	def test_retrieve(self):
		self.assertEqual(self.pm.retrieve('test123'), {'num': 123})




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

	def test_parse(self):
		raw_data = """        intervals [3]:
            xmin = 2.29 
            xmax = 6.720125 
            text = "1第一块"
        intervals [4]:
            xmin = 0
            xmax = 6.720125 
            text = "2第二块"
		"""
		with patch('parse_textgrid.TextgridParser.lines', new_callable=PropertyMock, create=True) as mock_lines:
			mock_lines.return_value = raw_data.splitlines()
			intervals = self.tp.parse()
			self.assertEqual(len(intervals), 2)
			self.assertEqual(intervals[0]['text'], u"1第一块".encode('utf-8'))
			self.assertEqual(intervals[1]['text'], u"2第二块".encode('utf-8'))

	def test_real_file(self):
		# self.tp.feed('/Users/imac/Desktop/1.TextGrid')
		self.tp.feed('/Users/imac/Downloads/test_3layers.TextGrid')
		self.tp.parse()