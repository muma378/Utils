# -*- coding: utf-8 -*-

import os
import unittest
import mock

from qualify_textgrid import TextgirdParser, CycleIterator
from qualify_textgrid import validate

class TextgirdParserTextCase(unittest.TestCase):
	"""test case for TextgirdParser"""
	def setUp(self):
		self.tp = TextgirdParser()

	@mock.patch('__builtin__.open')
	def test_read(self, mock_open):
		mock_open.return_value.__enter__ = lambda x: x
		mock_open.return_value.__exit__ = mock.Mock()
		self.tp.read()
