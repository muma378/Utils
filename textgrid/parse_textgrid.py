import re
import chardet

from log import LogHandler
logger = LogHandler('textgrid_parser.log', stdout=True)



class BlockIterator(object):
	"""
	iterators to control the flow of program
	"""
	def __init__(self, owner, ctrls, *patterns):
		super(BlockIterator, self).__init__()
		self.owner = owner
		self.start, self.end, self.error = ctrls 
		self.patterns = patterns
		self.index = 0
		
	def __iter__(self):
		for pattern in self.patterns:
			yield pattern

	# when returns an instance of BlockIterator, it means the block_iter in use will be replaced now
	# at this time, we reset the value of index
	def _reset_if_return(fn):
		def reset(self, *args):
			return_value = fn(self, *args)
			if return_value:
				self.index = 0
			return return_value
		return reset

	@property
	def head(self):
		return self.patterns[0]


	def next(self):
		pattern = self.patterns[self.index]
		self.index += 1
		return pattern

	@_reset_if_return
	def exit(self):
		return self.owner.get(self.end[0])

	def match_start(self, line):
		return self.trail(line, self.start)

	def match_error(self, line):
		return self.trail(line, self.error)

	@_reset_if_return
	def trail(self, line, candidate):
		for block_name in candidate:
			block_iter = self.owner.get(block_name)
			if block_iter.head.match(line):
				return block_iter
		return None


class DataBlock(object):
	def __init__(self, parent):
		self.parent = parent
		self.data = {}

	def end(self):
		self.parent.append(self.data)

	def update(self, key_val):
		self.data.update(key_val)



class PatternManager(object):
	def __init__(self, pattern, key, key_type):
		self.parser = re.compile(pattern)
		self.key = key
		self.key_type = key_type

	def match(self, line):
		return self.parser.match(line)

	def retrieve(self, line):
		# process when self.key was not None
		if self.key:
			self.result = self.match(line)
			if self.result:
				return {self.key: self.key_type(self.result.group(self.key))}
		else:
			return {}	# sentinel, no effect on dict.update


# to parse the textgrid as more as we can, data structure descibed below was created to indicate the flow;
# In each variable which is similar to *_BLOCK, first tuple listed gives information about what to match for some special cases;
# 1. the first one indicates what pattern to test before matching the current one, 
#    usually, it is empty, and only needed when the pattern was like '^(?P<text>.*)$', such as MULTILINES_BODY_BLOCK;
# 2. the second stands for what block to use after traversing all patterns in the original. Noted only one exit is necessary;
# 3. the third describes what blocks to try on if an unmatched exception happened;
class TextgridParser(object):
	"""translate the textgrid into a dict"""
	# for textgrid header
	HEADER_BLOCK= (
		# list possible next stops in sequence so that interpreter knows where to match when it ends
		# if it doesn't match any patterns listed in the tuple, it would pop to the last entry
		((), ('ITEM_BLOCK', ), ('ITEM_BLOCK', 'HEADER_BLOCK'), ),
		('^xmin = (?P<xmin>[\d\.]+)', 'xmin', float),
		('^xmax = (?P<xmax>[\d\.]+)', 'xmax', float),
		('^tiers\? <exists>', None, type(None)),
		('^size = (?P<size>\d+)', 'size', int),
		('^item \[\]: ', None, type(None)),
		)

	ITEM_BLOCK = (
		((), ('INTERVAL_BLOCK', ), ('INTERVAL_BLOCK', 'ITEM_BLOCK')),
		('^\s*item \[(?P<item>\d+)\]:', 'item', str),
        ('^\s*class = "(?P<class>\w+)"', 'class', str), 
        ('^\s*name = "(?P<name>\w*)"', 'name', str),
        ('^\s*xmin = (?P<xmin>[\d\.]+)', 'xmin', float),
		('^\s*xmax = (?P<xmax>[\d\.]+)', 'xmax', float),
        ('^\s*intervals: size = (?P<size>\d+)', 'size', int),
		)

	# a block stands for each interval in an item
	INTERVAL_BLOCK = (
		((), ('INTERVAL_BLOCK', ), ('INTERVAL_BLOCK', 'MULTILINES_HEAD_BLOCK', 'ITEM_BLOCK', )),
		('^\s*intervals \[(?P<slice>\d+)\]:', 'slice', int),
		('^\s*xmin = (?P<xmin>[\d\.]+)', 'xmin', float),
		('^\s*xmax = (?P<xmax>[\d\.]+)', 'xmax', float),
		('^\s*text = "(?P<text>.*)"', 'text', str),
		)
	# for a special case that one text has multiple lines
	MULTILINES_HEAD_BLOCK = (
		((), ('MULTILINES_BODY_BLOCK', ), ('INTERVAL_BLOCK', 'ITEM_BLOCK',)),
		('^\s*text = "(?P<text>.*)', 'text', str),
	)

	# stack is not available here cause the pattern matches text whatever it is
	# therefore we have to list all possible next stops in case of error occured here
	MULTILINES_BODY_BLOCK = (
		(('MULTILINES_TAIL_BLOCK', 'INTERVAL_BLOCK', 'ITEM_BLOCK',), ('MULTILINES_BODY_BLOCK', ), ()),
		('^(?P<text>.*)$', 'text', str),	# to adapt the new line
	)

	MULTILINES_TAIL_BLOCK = (
		# impossible to trigger an unmatched exception, cause the pattern was entered only if it was matched
		((), ('INTERVAL_BLOCK', ), ()),
		('^(?P<text>.*)"\s*$', 'text', str),
	)

	BLOCK_SUFFIX = '_BLOCK'

	def __init__(self, encoding='utf-8'):
		super(TextgridParser, self).__init__()
		self.encoding = encoding
		self.__package()
		self.entry = self.HEADER_BLOCK

	# to initialize BlockIterator and PatternManager with static variables
	def __package(self):
		for key, args in type(self).__dict__.items():
			if key.endswith(self.BLOCK_SUFFIX):
				block_iter_args = [args[0], ]
				for pattern_manager_args in args[1:]:
					block_iter_args.append(PatternManager(*pattern_manager_args))
				
				setattr(self, key, BlockIterator(self, *block_iter_args))

	def get(self, name):
		return self.__dict__[name]			
		
	def feed(self, filename):
		try:
			self.filename = filename.decode('gb2312')	# TODO: to test
			logger.info('processing file: %s' % self.filename)
		except UnicodeDecodeError, e:
			self.filename = filename
			logger.info('processing file ...')

		with open(filename, 'rb') as f:
			raw_data = f.read()
			self.decoding = chardet.detect(raw_data)['encoding']
			try:
				self.content = raw_data.decode(self.decoding).encode(self.encoding)
				self.lines = self.content.splitlines()
			except UnicodeError, e:
				logger.error('unable to decode file %s, please open with a text editor and save it with encoding utf-8' % self.filename)
				raise e


	def parse(self):
		lineno, data, block_iter = 0, {}, self.entry
		freeze = False
		for line in self.lines:
			lineno += 1	

			matched_block = block_iter.match_start(line)
			if matched_block:
				block_iter = matched_block

			if not freeze:
				try:
					pattern_manager = block_iter.next()
				except IndexError, e:
					block_iter = block_iter.exit()
					pattern_manager = block_iter.next()

			# match patterns in error if it no patterns matched
			if not pattern_manager.match(line):
				matched_block = block_iter.match_error(line)
				if matched_block:
					block_iter = matched_block
					pattern_manager = block_iter.next()
				else:
					# matches nether current parrten nor possible block
					logger.info('unabel to match %s at line %d' % (line, lineno))
					freeze = True
					continue

			print pattern_manager.retrieve(line)	# TODO: which data set to use
			freeze = False


