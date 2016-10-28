import re
import os
import sys
sys.path.append(".")

from base.traverse import traverser


FILENAME = 'matched-results.txt'
REGEXP = "\[[^[]+?\]\S+|\{[^{]+?\}\S+|"
REGEXP += "\[.+?\]|\{.+?\}|\{.+?\]|\[.+?\}|\(.+?\)" 


def lookup(dir_name, regexp, container):
	for filename, _ in traverser(dir_name, '', 'txt'):
		with open(filename, 'r') as f:
			for line in f:
				matched_list = re.findall(regexp, line)
				container.update(matched_list)
	return container


if __name__ == '__main__':
	dir_name = sys.argv[1]
	matched_set = set()
	lookup(dir_name, REGEXP, matched_set)
	with open(FILENAME, 'w') as f:
		for exp in matched_set:
			f.write(exp)
			f.write('\n')
		# f.write(matched_set)
