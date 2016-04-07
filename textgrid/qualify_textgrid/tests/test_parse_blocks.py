# -*- coding: utf-8 -*-
import os
import shutil
import unittest
from mock import patch, PropertyMock
from parse_blocks import TextgridBlocksParser

class TextgridParserTestCase(unittest.TestCase):
	def setUp(self):
		self.tp = TextgridBlocksParser()

	def test_read(self):
		filenames = ('temp1.txt', 'temp2.txt', 'temp3.txt', 'temp4.txt')
		raw_data = ('hello,test', u'测试utf-8', u'测试utf-16-le', u'测试utf-16-be')
		codings = ('ascii', 'utf-8', 'utf-16', 'gb2312')

		def generate_files(filename, raw_data, coding):
			with open(filename, 'w') as f:
				f.write(raw_data.encode(coding))
		
		for i in range(len(raw_data)):
			generate_files(filenames[i], raw_data[i], codings[i])	
			self.tp.read(filenames[i])
			# self.assertEqual(self.tp.content, raw_data[i].encode('utf-8'))
			os.remove(filenames[i])


	def test_parse_blocks(self):
		raw_data = """        intervals [3]:
            xmin = 2.29 
            xmax = 6.720125 
            text = "1测试单行" 
		"""
		with patch('parse_blocks.TextgridBlocksParser.lines', new_callable=PropertyMock, create=True) as mock_lines:
			mock_lines.return_value = raw_data.splitlines()
			interval = self.tp.parse_blocks()[0]
			self.assertEqual(interval['slice'], 3)
			self.assertEqual(interval['xmin'], 2.29)
			self.assertEqual(interval['xmax'], 6.720125)
			self.assertEqual(interval['text'], u'1测试单行'.encode('utf-8'))

	def test_parse_multilines(self):
		raw_data = """        intervals [3]:
            xmin = 2.29 
            xmax = 6.720125 
            text = "1测试多行
            第二行
            第三行" 
		"""
		with patch('parse_blocks.TextgridBlocksParser.lines', new_callable=PropertyMock, create=True) as mock_lines:
			mock_lines.return_value = raw_data.splitlines()
			interval = self.tp.parse_blocks()[0]
			self.assertEqual(interval['text'], u'1测试多行\
            第二行\
            第三行'.encode('utf-8'))

	def test_incorrect_block(self):
		raw_data = """        intervals [3]:
            xmin = 2.29 
            xmax = 6.720125 
            text = "1测试多行
            第二行
		"""
		with patch('parse_blocks.TextgridBlocksParser.lines', new_callable=PropertyMock, create=True) as mock_lines:
			mock_lines.return_value = raw_data.splitlines()
			intervals = self.tp.parse_blocks()
			self.assertEqual(len(intervals), 0)

	def test_ignore_incorrect(self):
		raw_data = """        intervals [3]:
            xmin = 2.29 
            xmax = 6.720125 
            text = "1测试多行
        intervals [4]:
            xmin = 0
            xmax = 6.720125 
            text = "1测试"
		"""
		with patch('parse_blocks.TextgridBlocksParser.lines', new_callable=PropertyMock, create=True) as mock_lines:
			mock_lines.return_value = raw_data.splitlines()
			interval = self.tp.parse_blocks()[0]
			self.assertEqual(interval['text'], u'1测试'.encode('utf-8'))

	def test_blank_value(self):
		raw_data = """        intervals [3]:
            xmin = 2.29 
            xmax =  
            text = "1测试"
		"""
		with patch('parse_blocks.TextgridBlocksParser.lines', new_callable=PropertyMock, create=True) as mock_lines:
			mock_lines.return_value = raw_data.splitlines()
			intervals = self.tp.parse_blocks()
			self.assertEqual(len(intervals), 0)

	def test_multi_blocks(self):
		raw_data = """        intervals [3]:
            xmin = 2.29 
            xmax = 6.720125 
            text = "1第一块"
        intervals [4]:
            xmin = 0
            xmax = 6.720125 
            text = "2第二块"
		"""
		with patch('parse_blocks.TextgridBlocksParser.lines', new_callable=PropertyMock, create=True) as mock_lines:
			mock_lines.return_value = raw_data.splitlines()
			intervals = self.tp.parse_blocks()
			# import pdb;pdb.set_trace()
			self.assertEqual(len(intervals), 2)
			self.assertEqual(intervals[0]['text'], u"1第一块".encode('utf-8'))
			self.assertEqual(intervals[1]['text'], u"2第二块".encode('utf-8'))


	def test_parse_header(self):
		raw_data = """File type = "ooTextFile"
Object class = "TextGrid"

xmin = 0 
xmax = 601.551125 
tiers? <exists> 
size = 1 """
		with patch('parse_blocks.TextgridBlocksParser.content', new_callable=PropertyMock, create=True) as mock_content:
			mock_content.return_value = raw_data
			# self.tp.parse_header()
			# self.assertEqual(self.tp.original_duration_sum, 601.551125)

