# -*- coding: utf-8 -*-
import os
import sys
import re
import xml.etree.ElementTree as ET

import textgrid_generator as tg

# eg. 110#$260#$做个预告，$#260#$440#$稍$#78920#$79240#$绽放》。$#
def parse(xml_string, tag='speech', sep='$#'):
	root = ET.fromstring(xml_string)
	data = root.find(tag).text
	xml_parser = re.compile('^(?P<xmin>\d*)#\$(?P<xmax>\d*)#\$(?P<text>.*?)$', re.UNICODE)

	intervals = []
	for interval_str in data.strip().split(sep):
		try:
			intervals.append(xml_parser.match(interval_str).groupdict())
		except AttributeError, e:
			print('unable to parse %s' % interval_str)

	return intervals

# to concetrate words into phrase
def concetrate(intervals, sentence_stop=u'[。，！？”]'):
	phrase_list = [{'xmin': 0, 'xmax':0, 'text':'', 'slice':0}, ]
	phrase_parser = re.compile("(?P<stop>.*?"+sentence_stop+u')(\w+：)?(?P<text>\w*)', re.UNICODE)

	index = 0
	for word in intervals:
		result = phrase_parser.match(word['text'])
		phrase = phrase_list[index]
		if result:
			phrase['text'] += result.group('stop')
			
			index += 1
			next_phrase = {'xmin': int(word['xmin'])/1000.0, 'xmax': int(word['xmax'])/1000.0, 'text':result.group('text'), 'slice': index}
			phrase_list.append(next_phrase)
		
		else:
			phrase['xmax'] = int(word['xmax'])/1000.0
			phrase['text'] += word['text']
	
	return phrase_list


def main(filename):
	with open(filename, 'rb') as f:
		data = f.read()
	intervals = parse(data, 'speech')
	phrases = concetrate(intervals)
	with open(filename.replace('.xml', '.textgrid'), 'w') as f:
		slices = tg.prefill_slices(phrases)
		f.write(tg.generate_output(slices))

if __name__ == '__main__':
	main(sys.argv[1])