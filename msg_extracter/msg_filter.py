# -*- coding: utf-8 -*-
import os
import re
from jieba import posseg as pseg
from pyspark import SparkConf, SparkContext

import settings

# each rule stands for a conbination in the tuple
# such as ('t|m', 'v'), which indicates that 
# the line's tags were ought to contain 't' or 'm', then and 'v'
def rules_interpret(rule):
	syntax_parser = re.compile('.*'.join(rule))
	return lambda line: syntax_parser.search(line)

def word_segment(line):
	tags = [ tag for word, tag in pseg.cut(line) ]
	return (line, "".join(tags))

# TODO: look up the file to be processed in sqlite3
def target_files():
	return (os.path.join(settings.DATA_DIRECTORY, 'demo.txt'), 
		os.path.join(settings.SAVE_DIRECTORY, '12.txt'))

def filter_msgs(src_file, dst_file, category):
	# TODO: rename app name for the project
	conf = SparkConf().setMaster(settings.MASTER_URL).setAppName(settings.APP_NAME)
	conf.setAll([("spark.eventLog.enabled", "true"), ("spark.eventLog.dir", settings.LOG_DIRECTORY)])

	valid_tags = rules_interpret(settings.SYNTAX_RULES[category])

	# TODO:run several textfiles in parallel
	sc = SparkContext(conf=conf)
	rdd = sc.textFile(src_file)
	valid_words = rdd.map(word_segment).filter(lambda pair: valid_tags(pair[1])).map(lambda x: x[0])
	
	valid_words.persist()
	valid_words.saveAsTextFile(dst_file)
	# return valid_words.collect()

