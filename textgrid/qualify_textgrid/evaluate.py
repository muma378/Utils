# -*- coding: utf-8 -*-
import re
from settings import logger
import settings

class RulesCensor(object):
	def __init__(self, rules):
		self.rules = rules
		# logger.info("initialize RulesCensor with rules " + str(rules))
		self.decoding = 'utf-8'
		self.qualified = []
		self.errors = []

	def validate(self, intervals):
		for interval in intervals:
			legal = True
			text = interval[settings.INTERVAL_KEY_TEXT]
			if text:
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
		return self.qualified


class Calculagraph(object):
	def __init__(self):
		self.category_parser = re.compile('^(?P<category>[1-4])\D.*', flags=re.UNICODE)
		self.pattern_key = 'category'
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

	def prints(self, unit='s', title=None):
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
