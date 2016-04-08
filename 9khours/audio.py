# -*- coding: utf-8 -*-
# audio.py - usage: 
# class to provide interface to process common operation
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.11

import os
import sys
import wave
import math
from struct import pack, unpack

from log import LogHandler
logger = LogHandler('audio_process.log', stdout=True)


class Wave(object):

	PACKTYPE = { 
		1: 'c',
		2: 'h',
		4: 'l',
		8: 'q',
	}

	PACKENDIAN = {
		'little': '<',
		'big':'>',
	}

	def __init__(self, filename, header, content):
		self.filename = filename
		self.header = header
		self.nchannels, self.samplewidth, self.framerate, self.nframes = self.header[0:4] 
		self.content = content

	# get the format for packing or unpacking, like '<iiii'
	def _get_packfmt(self):
		# TODO: not sure how byte arrange in stereo
		return Wave.PACKENDIAN[sys.byteorder] + Wave.PACKTYPE[self.samplewidth] * self.nframes * self.nchannels

	def unpack(self):	
		try:
			return self.unpacked_content
		except AttributeError, e:
			self.unpacked_content = unpack(self._get_packfmt(), self.content)
		return self.unpacked_content

	def pack(self, frames):
		self.content = pack(self._get_packfmt(), *frames)
		return self.content

	def partial_pack(self, frames_num, frames):
		return pack(Wave.PACKENDIAN[sys.byteorder]+Wave.PACKTYPE[self.samplewidth]*frames_num*self.nchannels, frames)

	def partial_unpack(self, frames_num, content):
		return unpack(Wave.PACKENDIAN[sys.byteorder]+Wave.PACKTYPE[self.samplewidth]*frames_num*self.nchannels, content)

	def get_duration(self):
		return float(self.nframes)/(self.nchannels*self.framerate)

	def time2frames(self, duration):
		return self.framerate * self.nchannels * duration

	def frames2bytes(self, frames):
		return frames * self.samplewidth

	def time2bytes(self, duration):
		return self.samplewidth * self.framerate * self.nchannels * duration

	def bytes2frames(self, bytes):
		return long(bytes/self.samplewidth)

	def lower_sampling(self, low_framerate=8000):
		step = int(self.framerate / low_framerate)
		if step > 1:	# make sure the new framerate is lower than the original
			sample = self.unpack()[0::step]
		self.nframes = self.nframes / 2
		self.framerate = low_framerate
		self.header = self.header[0:2]+(self.framerate, self.nframes,)+self.header[4:]
		self.pack(sample)
		return sample

	# this voice segmentation algorithm is based on energy estimation 
	# which refered to :
	# Rocha R B, Freire V V, Alencar M S. Voice segmentation system based on energy estimation[C]
	# Signal Processing Conference (EUSIPCO), 2014 Proceedings of the 22nd European. IEEE, 2014: 860-864.
	def voice_segment(self, window_duration=0.01, offset_duration=0.1):
		window_size = self.framerate * window_duration  # 10ms for each window
		assert(window_size==int(window_size))
		window_size = int(window_size)

		windows = []
		for i in xrange(1, self.nframes, window_size):
			windows.append(map(lambda x: float(x)*float(x), self.unpack()[i:i+window_size]))

		normalized_frames = []
		for window in windows:
			avg_window_energy = sum(window) / window_size
			
			for energy in window:
				if energy > avg_window_energy:
					normalized_frames.append(1)
				else:
					normalized_frames.append(0)
		
		offset_size = self.framerate * offset_duration
		
		borders, flip = [0], False
		continuous_times = 0
		last_status = 0
		for i, current_status in enumerate(normalized_frames):
			if last_status == current_status:
				continuous_times += 1
			else:
				last_status = current_status
				continuous_times = 0

			if continuous_times == offset_size:
				borders.append(i)

		print map(lambda x: float(x)/self.framerate, borders)
		print len(borders)



class WaveWriter(Wave):
	def __init__(self, filename, header, content):
		super(WaveWriter, self).__init__(filename, header, content)

	def write(self, mode='wb', quiet=True):
		if not quiet and os.path.exists(self.filename):
			logger.info('file %s was overrided' % self.filename)
		wav = wave.open(self.filename, mode)
		wav.setparams(self.header)
		wav.writeframesraw(self.content)
		wav.close()


class WaveReader(Wave):
	def __init__(self, filename):
		self.wav = self.open(filename)
		super(WaveReader, self).__init__(filename, self.wav.getparams(), self.wav.readframes( self.wav.getparams()[3]))
		self.sections = [Wave(filename, self.header, self.content)]
		self.wav.close()

	def open(self, filename, mode='rb'):
		wav = wave.open(filename, mode)
		return wav

	def name_section(self, index):
		return self.filename[:-4] + '_' + str(index) + '.wav'

	# truncate chunks if it was over the specified duration
	def truncate(self, duration):
		sub_section_frames = self.time2frames(duration)
		sub_section_bytes = self.frames2bytes(sub_section_frames)
		total_frames, self.sections = self.nframes, []
		index = 0
		while total_frames > 0:
			# append the whole frames if it was below the specified duration
			if total_frames < sub_section_frames:
				sub_section_frames = total_frames
			
			total_frames -= sub_section_frames

			start_byte = index * sub_section_bytes 
			self.sections.append( Wave(self.name_section(index), 
				self.header[0:3]+(sub_section_frames,)+self.header[4:],
				self.content[start_byte:start_byte+sub_section_bytes]) )
			index += 1

		return self.sections

	def smart_truncate(self, duration, window=0.5, threshold=200.0):
		window_bytes = self.time2bytes(window)
		section_bytes = self.time2bytes(duration)
		total_bytes = self.frames2bytes(self.nframes)
		
		if section_bytes > total_bytes:
			return self.sections

		self.sections = []
		end_byte = 0
		index = 0
		offset_time = 0.1

		window_frames = self.bytes2frames(window_bytes)
		while end_byte < total_bytes:
			start_byte = end_byte
			# append the whole frames if it was below the specified duration
			if total_bytes < start_byte + section_bytes:
				end_byte = total_bytes
			else:
				offset = 0
				end_byte = start_byte + section_bytes
				while True:
					# if no avaible offset found, take it 
					if end_byte-window_bytes-offset < start_byte:
						threshold = threshold * 2
						offset = 0

					boundary = self.content[long(end_byte-window_bytes-offset):long(end_byte-offset)]
					packed_boundary = self.partial_unpack(window_frames, boundary)
					abs_boundary = map(lambda x: math.fabs(x), packed_boundary)
					
					if sum(abs_boundary) > threshold * window_frames:
						offset += self.time2bytes(offset_time)
					else:
						end_byte = long(end_byte - offset)
						break
 
 			section_frames = self.bytes2frames(end_byte-start_byte)
			self.sections.append( Wave(self.name_section(index), 
				self.header[0:3]+(section_frames,)+self.header[4:],
				self.content[start_byte:end_byte]))
			index += 1

		return self.sections




