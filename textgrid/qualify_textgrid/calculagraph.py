# -*- coding: utf-8 -*-
# calculagraph.py - usage: from calculagraph import Calculagraph; cg = Calculagraph()
# to calculate duration for intervals	
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.April.14


import re
from settings import logger
import settings

class Calculagraph(object):
	TIME_UNIT = {
		's':(1, u'秒'),
		'm':(60.0, u'分'),
		'h':(3600.0, u'小时')
	}

	DEFAULT_PATTERN = re.compile('.*', re.UNICODE)

	"""calculate duration if it matches the pattern"""
	def __init__(self, match_parser=None):
		super(Calculagraph, self).__init__()
		self.match_parser = match_parser if match_parser else self.DEFAULT_PATTERN	# matchs all by default
		self.errors = []

	def measure(self, intervals):
		self.duration = 0.0
		for interval in intervals:
			try:
				if self.match_parser.match(interval[settings.INTERVAL_KEY_TEXT]):
					time_len = interval[settings.INTERVAL_KEY_XMAX] - interval[settings.INTERVAL_KEY_XMIN]
					if time_len < 0:
						self.errors.append(u'错误: 在第%d行检测到xmax的值大于xmin值' % interval[settings.INTERVAL_KEY_LINENO])
					else:
						self.duration += time_len

			except AttributeError, e:
				logger.error("unable to parse the text: %s at line %d" % (interval[settings.INTERVAL_KEY_TEXT], interval[settings.INTERVAL_KEY_LINENO]))
				continue 
				
		return self.duration

	def get_unit_display(self, unit):
		try:
			divider, unit_display = self.TIME_UNIT[unit]
		except KeyError, e:
			logger.error('unknown choice "%s" for unit' % unit)
			raise e
		return divider, unit_display

	def output_duration(self, unit='s'):
		output = []
		divider, unit_display = self.get_unit_display(unit)
		output.append(u"有效时长为%f%s" % (self.duration/divider, unit_display))
		return output


class CategoricalCalculagraph(Calculagraph):
	"""calculate duration for different categories respectively"""
	def __init__(self, category_parser, pattern_key, category_display=None):
		super(CategoricalCalculagraph, self).__init__()
		self.category_parser = category_parser
		self.pattern_key = pattern_key
		self.category_display = category_display if category_display else settings.MARKS_MEANING

	def measure(self, intervals):
		self.assorted = {}
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

	def output_duration(self, unit='s'):
		output = []
		divider, unit_display = self.get_unit_display(unit)
		try:
			for key, val in self.assorted.items():
				output.append(u'%s时长为%f%s' % (self.category_display[key], val/divider, unit_display))
		except KeyError, e:
			logger.error('marks included are not supported')

		return output