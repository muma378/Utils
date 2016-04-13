# -*- coding: utf-8 -*-
from settings import logger
import settings

# check if text in each interval is qualified
class RulesCensor(object):
	def __init__(self, rules):
		self.rules = rules
		logger.info("initialize RulesCensor with rules " + str(rules))
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

