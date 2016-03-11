# -*- coding: utf-8 -*-
# generate_scenario_xml.py - usage: python generate_scenario_xml.py settings.txt
# to generate 5 scenario.xml according content in settings.txt
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.10

import re
import sys

stage_xml = """    <stage>
      <index>{counter}</index>
      <name>gesture {counter}</name>
      <description>{desc}</description>
      <length>{length}</length>
      <example>C:\\temp\example\{expression}\{counter}.png</example>
      <tag>{expression} {gesture}</tag>
    </stage>
"""

expression_set = ['neutral', 'happy', 'sad', 'surprise', 'anger']
default_desc = '{expression} {gesture}'
default_length = '60'
gestures = [('frontal', '150', 'neutral frontal in 5 sec', 'neutral'), 
			('frontal', '300', '{expression} {gesture} in 10 sec'),
			('yaw left',),
			('frontal',),
			('yaw right',),
			('frontal',),
			('pitch up',),
			('frontal',),
			('pitch down',),
			('frontal',),
			('roll left',),
			('fronal',),
			('roll right',),
			('frontal', '150', 'neutral frontal in 5 sec', 'neutral'),
			]

def generate(filename):
	with open(filename, 'r') as f:
		scenerio_xml = f.read()
	for scenario in expression_set:
		stages = ''
		scenerio_file = 'scenario-'+scenario+'.xml'
		capital = scenario.capitalize()
		for counter, stage_info in enumerate(gestures, start=1):
			gesture, length, desc, expression = get_stage_args(stage_info, scenario)
			stages += stage_xml.format(**locals())

		with open(scenerio_file, 'w') as s:
			s.write(scenerio_xml.format(capital=capital, stages=stages))


def get_stage_args(stage_info, expression):
	gesture = stage_info[0]
	if len(stage_info) == 1:
		return gesture, default_length, default_desc.format(**locals()), expression
	elif len(stage_info) == 3:
		return gesture, stage_info[1], stage_info[2].format(**locals()), expression
	elif len(stage_info) == 4:
		return stage_info
	else:
		print "illegal format"
		sys.exit(0)


if __name__ == '__main__':
	generate(sys.argv[1])