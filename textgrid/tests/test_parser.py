# -*- coding: utf-8 -*-
import os
import shutil
import unittest
from mock import patch, PropertyMock
from parse_textgrid import TextgridParser

class TextgridParserTestCase(unittest.TestCase):
	def setUp(self):
		self.tp = TextgridParser()

	def test_read(self):
		filenames = ('temp1.txt', 'temp2.txt', 'temp3.txt', 'temp4.txt')
		raw_data = ('hello,test', u'测试utf-8', u'测试utf-16-le', u'测试utf-16-be')
		codings = ('ascii', 'utf-8', 'utf-16-le', 'utf-16-be')

		def generate_files(filename, raw_data, coding):
			with open(filename, 'w') as f:
				f.write(raw_data.encode(coding))
		
		for i in range(len(raw_data)):
			generate_files(filenames[i], raw_data[i], codings[i])	
			self.tp.read(filenames[i])
			self.assertEqual(self.tp.lines[0], raw_data[i].encode('utf-8'))
			# self.assertEqual(self.tp.coding, codings[i])
			os.remove(filenames[i])


	def test_parse_blocks(self):
		raw_data = """        intervals [3]:
            xmin = 2.29 
            xmax = 6.720125 
            text = "1这几天嘛我不是跟你说过我有个很好的以前初中有个很好的朋友嘛" 
		"""
		with patch('TextgridParser.lines', new_callable=PropertyMock) as mock_lines:
			mock_lines.return_value = raw_data.splitlines()
			self.tp.parse_blocks()
			interval = self.tp.intervals[0]
			import pdb;pdb.set_trace()
			self.assertEqual(interval['slice'], 3)
			self.assertEqual(interval['xmin'], 2.29)
			self.assertEqual(interval['xmax'], 6.720125)
			self.assertEqual(interval['text'], u'1这几天嘛我不是跟你说过我有个很好的以前初中有个很好的朋友嘛')

