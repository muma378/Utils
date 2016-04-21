# -*- coding: utf-8 -*-
# calculagraph.py - usage: from calculagraph import Calculagraph; cg = Calculagraph()
# to calculate duration for intervals	
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.April.14

import os
import re
import sys
import base
import operator
from settings import logger
import settings


class BaseCalculagraph(base.BaseEvaluator):
	TIME_UNIT = {
		's':(1, u'秒'),
		'm':(60.0, u'分'),
		'h':(3600.0, u'小时')
	}
	def __init__(self):
		super(BaseCalculagraph, self).__init__()
		self.errors = []
		self.msg=u"{duration_display}{unit_display}" + settings.LINESEP

	def measure(self, intervals):
		raise NotImplementedError

	def output_duration(self, fd=sys.stdout, unit='s'):
		raise NotImplementedError

	def get_unit_display(self, unit):
		try:
			divider, unit_display = self.TIME_UNIT[unit]
		except KeyError, e:
			logger.error('unknown choice "%s" for unit' % unit)
			raise e
		return divider, unit_display

	def output(self, fd, duration, msg=None, unit='s', **kwargs):
		divider, unit_display = self.get_unit_display(unit)
		if not msg:
			msg = self.msg
		fd.write(msg.format(duration_display=duration/divider, unit_display=unit_display, **kwargs).encode(settings.ENCODING))


class PatternCalculagraph(BaseCalculagraph):
	DEFAULT_PATTERN = re.compile('.*', re.UNICODE)

	"""calculate duration if it matches the pattern"""
	def __init__(self, match_parser=None):
		super(PatternCalculagraph, self).__init__()
		self.match_parser = match_parser if match_parser else self.DEFAULT_PATTERN	# matchs all by default
		self.msg = u"文件有效时长为{duration_display}{unit_display}" + settings.LINESEP

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
		return self	
		# return self.duration

	def output_duration(self, fd=sys.stdout, unit='s'):
		self.output(fd, self.duration, self.msg, unit)


class CategoricalCalculagraph(BaseCalculagraph):
	"""calculate duration for different categories respectively"""
	def __init__(self, category_parser, pattern_key, category_display=None):
		super(CategoricalCalculagraph, self).__init__()
		self.category_parser = category_parser
		self.pattern_key = pattern_key
		self.category_display = category_display if category_display else settings.MARKS_MEANING
		self.msg = u'{category}时长为{duration_display}{unit_display}' + settings.LINESEP	# extra argument is needed

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
				self.assorted[category] = time_len		# new category
			except AttributeError, e:
				logger.error("unable to parse the text: %s at line %d" % (interval[settings.INTERVAL_KEY_TEXT], interval[settings.INTERVAL_KEY_LINENO]))
				continue
		self.duration = self.assorted	# adaptor
		return self

	def output_duration(self, fd=sys.stdout, unit='s'):
		try:
			for key, val in self.duration.items():
				self.output(fd, val, self.msg, unit, category=self.category_display[key])	
		except KeyError, e:
			logger.error('marks included are not supported')

def dict_add(d1, d2):
	temp_dict = d2.copy()
	for k in d1.keys():
		temp_dict[k] = d1[k] + d2.get(k, 0)
	return temp_dict

class OverallCalculagraph(BaseCalculagraph):
	"""calculate the overall duration for all files listed"""
	def __init__(self, concrete_cal):
		super(OverallCalculagraph, self).__init__()
		self.add = operator.add  	# use + for most cases
		if type(concrete_cal).__name__ == "PatternCalculagraph":
			self.accum = 0
		elif type(concrete_cal).__name__ == "CategoricalCalculagraph":
			self.accum = {}
			self.add= dict_add
		else:
			raise NotImplementedError()

		self.concrete_cal = concrete_cal
		self.msg = u"文件夹内统计的总时长为:" + settings.LINESEP

	def measure(self, intervals):
		self.accum = self.add(self.accum, self.concrete_cal.measure(intervals).duration)
		return self

	def output_duration(self, fd=sys.stdout, unit='h'):
		fd.write(self.msg.encode(settings.ENCODING))
		self.concrete_cal.duration = self.accum
		self.concrete_cal.output_duration(fd, unit)
