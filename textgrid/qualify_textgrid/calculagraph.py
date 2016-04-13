# -*- coding: utf-8 -*-

import re
from settings import logger
import settings

class Calculagraph(object):
	"""calculate duration if it matches the pattern"""
	def __init__(self, match_parser=None):
		super(Calculagraph, self).__init__()
		self.match_parser = match_parser if match_parser else re.compile('.*', re.UNICODE)	# matchs all by default
	
	def measure(self, intervals):
		duration = 0
		for interval in intervals:
			try:
				if self.match_parser.match(interval[settings.INTERVAL_KEY_TEXT]):
					time_len = interval[settings.INTERVAL_KEY_XMAX] - interval[settings.INTERVAL_KEY_XMIN]
					if time_len < 0:
						self.errors.append(u'错误: 在第%d行检测到xmax的值大于xmin值' % interval[settings.INTERVAL_KEY_LINENO])
					else:
						duration += time_len

			except AttributeError, e:
				logger.error("unable to parse the text: %s at line %d" % (interval[settings.INTERVAL_KEY_TEXT], interval[settings.INTERVAL_KEY_LINENO]))
				continue 
				
		return duration
		



class CategoricalCalculagraph(Calculagraph):
	"""calculate duration for different categories respectively"""
	def __init__(self, category_parser, pattern_key):
		self.category_parser = category_parser
		self.pattern_key = pattern_key
		self.assorted = {}
		self.errors = []

	def measure(self, intervals):
		for interval in intervals:
			try:
				category = self.category_parser.match(interval[settings.INTERVAL_KEY_TEXT]).group(self.pattern_key)
				time_len = interval[settings.INTERVAL_KEY_XMAX] - interval[settings.INTERVAL_KEY_XMIN]
				if time_len < 0:
					self.errors.append(u'错误: 在第%d行检测到xmax的值大于xmin值' % interval[settings.INTERVAL_KEY_LINENO])
				else:
					self.assorted[category] += time_len
			except KeyError, e:
				self.assorted[category] = time_len
			except AttributeError, e:
				logger.error("unable to parse the text: %s at line %d" % (interval[settings.INTERVAL_KEY_TEXT], interval[settings.INTERVAL_KEY_LINENO]))
				continue

		# duration for all category
		return self.assorted

	def output_duration(self, unit='s', title=None):
		output = []
		if title:
			output.append(title)
		try:
			divider, unit_display = settings.TIME_UNIT[unit]
		except KeyError, e:
			logger.error('unknown choice "%s" for unit' % unit)
			return

		try:
			for key, val in self.assorted.items():
				output.append(u'%s时长为 %f%s' % (settings.MARKS_MEANING[key], val/divider, unit_display))
		except KeyError, e:
			logger.error('marks included are not supported')

		return output