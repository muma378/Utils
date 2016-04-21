# -*- coding: utf-8 -*-
import os
import utils
from parse_blocks import TextgridBlocksParser
from censor import RulesCensor
from calculagraph import *
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
		log_path = utils.get_log_path(settings.LOG_ERROR_TYPE_NAME, args.target)
		with open(log_path, 'w') as fd:
			for src_file, _ in utils.traverser(args.target, "", settings.LOOKUP_NAMES_PATTERN):
				intervals = self.tbp.read(src_file).parse_blocks()
				censor.validate(intervals)
				fd.write(">>" + src_file.decode(settings.DECODING).encode(settings.ENCODING) + ':' + os.linesep)
				censor.output_errors(fd)


	def timeit(self, args):
		print_action = []
		get_layer = lambda x: self.tbp.get_layer(x, args.layer)		# consume argument layer

		# consume argument action
		if settings.TIME_ACTION_SEPARATELY == args.action:
			cal = CategoricalCalculagraph(settings.CALCULAGRAPH_CATEGORY_PATTERN, settings.CALCULAGRAPH_CATEGORY_KEY)
		elif settings.TIME_ACTION_TOGETHER == args.action:
			cal = PatternCalculagraph(settings.CALCULAGRAPH_ANYTEXT_PATTERN)
		else:
			raise ValueError

		log_path = utils.get_log_path(settings.LOG_DURATION_TYPE_NAME, args.target)
		fd = open(log_path, 'w')
		cal_out = lambda x: cal.measure(x).output_duration(fd)

		# consumte arguments print_option
		if settings.TIME_PRINT_OPTION_NOT_EMPTY in args.print_option:
			print_action.append(cal_out)
		if settings.TIME_PRINT_OPTION_VALID in args.print_option:
			censor = RulesCensor(settings.CENSOR_RULES)
			print_action.append(lambda x: cal_out(censor.validate(x).qualified))
		if settings.TIME_PRINT_OPTION_TOTAL in args.print_option:
			all_cal = OverallCalculagraph(cal)
			print_action.append(lambda x: all_cal.measure(x))
		
		for src_file, _ in utils.traverser(args.target, "", settings.LOOKUP_NAMES_PATTERN):
			intervals = get_layer(self.tbp.read(src_file).parse_blocks())

			fd.write(">>" + src_file.decode(settings.DECODING).encode(settings.ENCODING) + ':' + os.linesep)
			for action in print_action:
				action(intervals)

		if "all_cal" in locals().keys():
			fd.write(">>" + args.target.decode(settings.DECODING).encode(settings.ENCODING) + ' ')
			all_cal.output_duration(fd)


	def correct(self, args):
		pass


	def run(self):
		for src_file, _ in utils.traverser(args.target, "", settings.LOOKUP_NAMES_PATTERN):
			intervals = self.tbp.read(src_file).parse_blocks()
			for transform in self.transformation:
				intervals = transform(intervals)
			for act in self.action:
				act(intervals)

