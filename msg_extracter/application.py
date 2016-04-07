# -*- coding: utf-8 -*-
import re

# each rule stands for a conbination in the tuple
# such as ('t|m', 'v'), which indicates that 
# the line's tags were ought to contain 't' or 'm', then and 'v'
def rules_interpret(rule):
	syntax_parser = re.compile('.*'.join(rule))
	return lambda line: syntax_parser.search(line)

def word_segment(line):
	from jieba import posseg as pseg
	tags = [ tag for word, tag in pseg.cut(line) ]
	return (line, "".join(tags))

# filter messages with spark
def filter_msgs(sc, src_file, dst_file, category):
	# generating the function to filter tags
	import settings
	valid_tags = rules_interpret(settings.SYNTAX_RULES[category])
	rdd = sc.textFile(src_file)
	# extracting words which satisfy syntax rules fot the category
	valid_words = rdd.map(word_segment).filter(lambda pair: valid_tags(pair[1])).map(lambda x: x[0])
	valid_words.saveAsTextFile(dst_file)