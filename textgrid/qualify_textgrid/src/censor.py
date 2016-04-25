# -*- coding: utf-8 -*-
import os
import sys
import base
import utils
from settings import logger
import settings


class BaseCensor(base.BaseEvaluator):
	def __init__(self):
		super(BaseCensor, self).__init__()

	def validate(self, intervals):
		raise NotImplementedError

	def output_errors(self, fd=sys.stdout):
		raise NotImplementedError


# check if text in each interval was qualified
class TextCensor(BaseCensor):
	def __init__(self, rules):
		self.rules = rules
		logger.info("initialize RulesCensor with rules :")
		for i, (pat, fn, msg) in enumerate(rules, start=1):
			logger.info(str(i) + '.' + pat.pattern + ';')

	def validate(self, intervals):
		self.qualified = []
		self.errors = []
		for interval in intervals:
			text = interval[settings.INTERVAL_KEY_TEXT]
			if text:
				legal = True
				for rp, fn, msg in self.rules:
					result = rp.match(text)
					if result:
						text = fn(result)
					else:
						self.errors.append(msg.format(lineno=interval[settings.INTERVAL_KEY_LINENO], 
												text=interval[settings.INTERVAL_KEY_TEXT]))
						legal = False
						break
				if legal:
					self.qualified.append(interval)
		return self

	def output_errors(self, fd=sys.stdout):
		for err_msg in self.errors:
			fd.write(err_msg.encode(settings.ENCODING) + os.linesep)
		fd.write((u"共检测到%d个错误" % len(self.errors)).encode(settings.ENCODING))
		fd.write(os.linesep + os.linesep)

# to validate intervals to see if it was written as the format
class FormatCensor(BaseCensor):
	def __init__(self, plugins, layer=0):
		super(FormatCensor, self).__init__()
		self.plugins = plugins
		self.layer = layer

	# intervals passed is ought to be classfied and sorted
	def validate(self, intervals):
		def call_plugin(interval):
			for plugin in self.plugins:
				plugin(self, interval)

		items = utils.get_items(intervals)
		if self.layer == 0:
			# to modify elem in the list instead of refering
			for i in range(len(items)):
				call_plugin(items[i])
		else:
			call_plugin(items[self.layer-1])
		
		self.qualified = utils.flat_items(items)
		return self

	def validate_continua(self, intervals):
		last_xmax = 0
		global_xmin = 0		# should start from 0
		global_xmax = intervals[-1][settings.INTERVAL_KEY_XMAX]
		for i, interval in enumerate(intervals, start=0):
			lineno = interval[settings.INTERVAL_KEY_LINENO]
			if interval[settings.INTERVAL_KEY_XMIN] > global_xmax:
				logger.info("value xmin %f at line %d is not in the range" % (interval[settings.INTERVAL_KEY_XMIN], lineno))
				intervals[i][settings.INTERVAL_KEY_XMIN] = last_xmax

			if interval[settings.INTERVAL_KEY_XMAX] > global_xmax:
				logger.info("value xmax %f at line %d is not in the range" % (interval[settings.INTERVAL_KEY_XMAX], lineno))
				try:
					next_xmin = intervals[i+1][settings.INTERVAL_KEY_XMIN]
					if next_xmin > global_xmax:		# however if the next one was over the global xmax again...
						raise IndexError
				except IndexError, e:
					next_xmin = last_xmax
				intervals[i][settings.INTERVAL_KEY_XMAX] = next_xmin

			if last_xmax != interval[settings.INTERVAL_KEY_XMIN]:	# broken
				logger.info("time line is broken at line %d" % lineno)	
				intervals[i][settings.INTERVAL_KEY_XMIN] = last_xmax

			if interval[settings.INTERVAL_KEY_XMIN] > interval[settings.INTERVAL_KEY_XMAX]:		# overlapped
				logger.info("value xmin is bigger than the value of xmax at line %d" % lineno)
				intervals[i][settings.INTERVAL_KEY_XMAX] = interval[settings.INTERVAL_KEY_XMIN]
			
			last_xmax = interval[settings.INTERVAL_KEY_XMAX]

		return intervals
