# -*- coding: utf-8 -*-
import os
import sys
import base
from settings import logger
import settings

# check if text in each interval was qualified
class RulesCensor(base.BaseEvaluator):
	def __init__(self, rules):
		self.rules = rules
		logger.info("initialize RulesCensor with rules " + str(rules))

	def validate(self, intervals):
		self.qualified = []
		self.errors = []
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
		return self

	def output_errors(self, fd=sys.stdout):
		for err_msg in self.errors:
			fd.write(err_msg.encode(settings.ENCODING) + os.linesep)
		fd.write((u"共检测到%d个错误" % len(self.errors)).encode(settings.ENCODING))
		fd.write(os.linesep + os.linesep)
