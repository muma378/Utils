

class TextgridParser(object):
	"""translate the textgrid into a dict"""
	CODINGS = (
		('utf-8-sig', (codecs.BOM_UTF8,)),
		('utf-16', (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)),
		('utf-32', (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)),
		)

	# for textgrid header
	HEADER_PATTERN = (
		re.compile('xmin = (?P<start>[\d\.]+)\s*xmax = (?P<end>[\d\.]+)\s*tiers\? <exists>'),
		lambda x: float(x.group('end')) - float(x.group('start')),
		)

	BLOCK_PATTERNS = (
		(re.compile('^\s*intervals \[(?P<slice>\d+)\]:'), 'slice', int),
		(re.compile('^\s*xmin = (?P<xmin>[\d\.]+)'), 'xmin', float),
		(re.compile('^\s*xmax = (?P<xmax>[\d\.]+)'), 'xmax', float),
		(re.compile('^\s*text = "(?P<text>.*)"'), 'text', str),
		)
	# for a special case that one text has multiple lines
	MULTILINES_PATTERN = (
		(re.compile('^\s*text = "(?P<text>.*)'), 'text', str),
		(re.compile('^(?P<text>.*)$'), 'text', str),	# to adapt the new line
		(re.compile('^(?P<text>.*)"\s*$'), 'text', str),
	)

	PATTERN_KEYS = ('pattern', 'key', 'type')

	def __init__(self, coding='utf-8'):
		super(TextgridParser, self).__init__()
		self.default_coding = coding
		self.intervals = []
		self.original_duration_sum = 0

	def reset(self):
		self.intervals = []

	def read(self, filename):
		self.filename = filename
		with open(filename, 'rb') as f:
			raw_data = f.read()
			# self.coding = self.code_det(content[0:10])
			self.coding = chardet.detect(raw_data)['encoding']
			try:
				self.content = raw_data.decode(self.coding).encode(self.default_coding)
				self.lines = self.content.splitlines()
			except UnicodeError, e:
				loginfo(u'>>文件：{filename}'.format(filename=self.filename), stdout=True)
				loginfo(u'解码时发生错误，请选择合适的文本编辑器，并以utf-8编码格式保存后，再运行此程序', stdout=True)
				loginfo('')
				raise IOError

	def code_det(self, headline, default='utf-8'):
		for enc,boms in TextgridParser.CODINGS:
			if any(headline.startswith(bom) for bom in boms): 
				return enc
		return default

	def pack(self, keys, tuples):
		package = []
		for vals in tuples:
			package.append({ keys[i]:vals[i] for i in range(len(keys)) })
		return package

	def update(self, interval, item_pattern, line, append_mode=False):
		ip = item_pattern
		if append_mode:
			# only for text
			interval[ip['key']] += ip['type'](ip['pattern'].match(line).group(ip['key']))
		else:
			interval.update({ ip['key']: ip['type'](ip['pattern'].match(line).group(ip['key'])) }) 
		return interval

	def match(self, item_pattern, line):
		return item_pattern['pattern'].match(line)

	def search(self, parser, fn):
		return fn(parser.search(self.content))

	def parse(self):
		print(u'正在解析{filename}...'.format(filename=self.filename))
		loginfo(u'>>文件：%s' % self.filename)
		original_duration = self.search(*TextgridParser.HEADER_PATTERN)
		self.original_duration_sum += original_duration
		logtime(u'>>文件：%s\t 原始语音时长为%f秒' % (self.filename, original_duration))
		
		lineno = 0
		interval = {}
		APPEND_MODE = False
		self.reset()
		bp_iter = CycleIterator(self.pack(TextgridParser.PATTERN_KEYS, TextgridParser.BLOCK_PATTERNS))
		mp_iter = CycleIterator(self.pack(TextgridParser.PATTERN_KEYS, TextgridParser.MULTILINES_PATTERN))

		block_begining = bp_iter.head()
		item_pattern = bp_iter.next()
		for line in self.lines:
			lineno += 1

			# reset the block parsing once the line matched the begining pattern
			if self.match(block_begining, line):
				# self.update(interval, block_begining, line)
				# not the start actually, exception occured in parsing last block
				if item_pattern != block_begining:
					loginfo(u'错误：无法解析第%d行，不是textgrid标准格式，已跳过' % (lineno-1), stdout=True)	# last line instead of the current
					interval = {}
					APPEND_MODE = False
					bp_iter.reset()
					item_pattern = bp_iter.next()
					
			# when a text existed in multiple lines
			elif APPEND_MODE:
				# import pdb;pdb.set_trace()
				if self.match(mp_iter.tail(), line): # match the pattern of end line
					self.update(interval, mp_iter.tail(), line, APPEND_MODE)
					interval['lineno'] = lineno
					self.intervals.append(interval)	# block ends
					interval = {}
					item_pattern = bp_iter.next()	# loop to the begining
					APPEND_MODE = False
					# 2. block ending
				else:
					# append the middle part of the text
					self.update(interval, mp_iter.index(1), line, APPEND_MODE) 
			
			# match the item in sequence
			if self.match(item_pattern, line):
				self.update(interval, item_pattern, line)

				# if the end of the block was matched
				if bp_iter.end():
					interval['lineno'] = lineno
					self.intervals.append(interval)
					interval = {}

				# loop to the begining
				item_pattern = bp_iter.next()
				# 1. block ending

			#　match the begining of multi-lines text instead of a single line
			elif self.match(mp_iter.head(), line):
				self.update(interval, mp_iter.head(), line)
				APPEND_MODE = True

