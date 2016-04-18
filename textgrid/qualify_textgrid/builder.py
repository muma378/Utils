# -*- coding: utf-8 -*-

import utils
from parse_blocks import TextgridBlocksParser
from censor import RulesCensor
from calculagraph import Calculagraph, CategoricalCalculagraph
from settings import logger
import settings

class OperationsBuilder(object):
	"""to build a sequence of operation according to args from command-line"""
	def __init__(self):
		super(OperationsBuilder, self).__init__()
		self.tbp = TextgridBlocksParser()
		self.transformation = []
		self.action = []

	def verify(self, args):
		self.args = args
		censor = RulesCensor(settings.CENSOR_RULES)


	def timeit(self, args):
		pass

	def run(self):
		for src_file, _ in utils.traverser(args.target, "", settings.LOOKUP_NAMES_PATTERN):
			intervals = self.tbp.read(src_file).parse_blocks()
			for transform in self.transformation:
				intervals = transform(intervals)
			for act in self.action:
				act(intervals)


def timeit(args):
	tbp = TextgridBlocksParser()
	calculagraph = 
	log_path = utils.get_log_path(settings.LOG_DURATION_TYPE_NAME, args.target)
	
	with open(log_path, 'w') as fd:
		for src_file, _ in utils.traverser(args.target, "", settings.LOOKUP_NAMES_PATTERN):
			tbp.read(src_file)
			intervals = tbp.parse_blocks()
			



def verify(args):
	tbp = TextgridBlocksParser()
	censor = RulesCensor(settings.CENSOR_RULES)

	log_path = utils.get_log_path(settings.LOG_ERROR_TYPE_NAME, args.target)
	with open(log_path, 'w') as fd:
		for src_file, _ in utils.traverser(args.target, "", settings.LOOKUP_NAMES_PATTERN):
			tbp.read(src_file)
			intervals = tbp.parse_blocks()
			censor.validate(intervals)
			fd.write(">>" + src_file.decode(settings.DECODING).encode(settings.ENCODING) + ':' + os.linesep)
			censor.output_errors(fd)