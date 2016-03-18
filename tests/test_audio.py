# -*- coding: utf-8 -*-

import os
import sys
import unittest
import wave
from mock import patch, PropertyMock
from audio import Wave, WaveReader

class WaveReaderTestCase(unittest.TestCase):
	def setUp(self):
		self.wr = WaveReader('tests/data/sample.wav')

	def test_header(self):
		self.assertEqual(self.wr.filename, 'tests/data/sample.wav')
		self.assertEqual(self.wr.nchannels, 1)
		self.assertEqual(self.wr.samplewidth, 2)	# byte width instead of bitwidth
		self.assertEqual(self.wr.framerate, 16000)
		self.assertEqual(self.wr.nframes, 28560)

	def test_duration(self):
		self.assertEqual(self.wr.get_duration(), 1.785)

	def test_get_packfmt(self):
		if os.name == 'posix' and os.name == 'nt':	# little endian for posix
			self.assertEqual(self.wr._get_packfmt()[:5], '<hhhh')

	def test_pack(self):
		with patch('audio.WaveReader.content', new_callable=PropertyMock, create=True) as mock_content:
			if self.wr.samplewidth == 2 and sys.byteorder == 'little':
				# only true if sample width was 2 and big-endian
				mock_content.return_value = '\x00\x01' * self.wr.nframes
				self.assertEqual(self.wr.unpack()[0], 256)	

	def test_lower_sampling(self):
		self.assertEqual(len(self.wr.lower_sampling(8000)), self.wr.nframes/2)

	def test_name_section(self):
		self.assertEqual(self.wr.name_section(0), 'tests/data/sample_0.wav')
		self.assertEqual(self.wr.name_section(100), 'tests/data/sample_100.wav')

	def test_truncate(self):
		self.assertEqual(len(self.wr.truncate(1)), 2)
		self.assertEqual(len(self.wr.truncate(10)), 1)

		sections = self.wr.truncate(1)
		self.assertEqual(sections[0].samplewidth, 2)
		self.assertEqual(sections[0].nframes, self.wr.framerate)
		self.assertEqual(sections[1].nframes, self.wr.nframes-self.wr.framerate)
		self.assertEqual(sections[1].unpack()[0], 134)

	def test_voice_segment(self):
		wr = WaveReader('tests/data/sample_big.wav')
		wr.voice_segment(0.01, 0.005)