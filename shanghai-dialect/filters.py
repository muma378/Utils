# -*- coding: utf-8 -*-

import sys
import re
from dp.core.base import regexp


class LabelsMatchBuilder(regexp.MatchBuilder):
	"""extracted if any of keywords was matched"""	
	def __init__(self):
		super(LabelsMatchBuilder, self).__init__()

	# rules = (regexp1, regexp2, ... )
	def build_rules(self, rules):
		self.regex.rules = []
		for rule in rules:
			self.regex.rules.append(re.compile(rule, re.UNICODE))

	def build_parser(self):

		def find_any(rules, line):
			for rule in rules:
				if rule.search(line):
					return True
			return False

		self.regex.parse = find_any


	def build_file_processor(self):

		def process_file(filename):
			collection = []
			with open(filename, 'r') as f:
				for line in f:
					text = line.strip().split('\t')[-1].decode('utf-8')
					if self.regex.process(text):
						collection.append(line)
			return collection

		self.regex.process_file = process_file


# PHONENUMBER_LABELS = ["\d{7}", "\d{11}"]

# CHINESE_NUMBERS = u"零一二三四五六七八九十廿"
# NUM = "["+CHINESE_NUMBERS+"\d]"
# TIMESTAMP_LABELS = ["\d{4}-\d{2}-\d{2}", "\d{4}/\d{2}/\d{2}", u"辰光", u"前天", u"昨日", 
# 	u"今朝", u"明朝", u"早浪", u"上半天", u"上半日", u"中浪", u"下半天", u"下半日", u"夜头", 
# 	u"夜里", u"夜到", u"钟头", u"几点", u"\d{1,2}点", u"\d{1,2}点\d{1,2}分", u"\d{1,2}点缺\d{1,2}分",
# 	NUM+u"{1,4}年", u"号头", NUM+u"{1,2}月"+NUM+u"{1,2}号",  NUM+u"月份", u"礼拜"+NUM, u"礼拜天"]
# IDENTITYCARD_LABELS = ["\d{17}[\dxX]"]
# CURRENCY_LABELS = [u"钞票", u"\d+块", u"\d+块头", u"几钿", u"\d+元", u"\d+角", u"美元", u"人民币", u"日元", 
# 	u"日币", u"欧元"]
# EMAIL_LABELS = ["[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}"]

# IDENTITYCARD_LABELS = [u"身份证",]
# EMAIL_LABELS = [u"邮箱", u"电子邮箱"]
PHONENUMBER_LABELS = [u"电话号", u"手机号", u"电话是多少", u"电话是撒", u"电话多少", "\d{7}", "\d{11}"]


if __name__ == '__main__':
	textfile = sys.argv[1]
	rd = regexp.RegexDirector(LabelsMatchBuilder())
	labelnames = filter(lambda x: x.endswith("_LABELS"), locals().keys())
	for label in labelnames:
		rules = locals().get(label)
		regex_proc = rd.construct(rules).get_regex_proc()
		result = regex_proc.process_file(textfile)
		with open(label+'.txt', "w") as f:
			f.write(''.join(result))


