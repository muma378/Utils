import re
import os
import sys

FILENAME = 'other_list.txt'

MATCHRULES = (
	re.compile(".*\[other\]\s*$"),
	)

def lookup(content):
	for parser in MATCHRULES:
		if parser.match(content):
			return True
	return False

def main(target):
	files = filter(lambda x: x.endswith(".txt"), os.listdir(target))
	with open(FILENAME, 'a') as w:
		for filename in files:
			filename = os.path.join(target, filename)
			with open(filename, 'r') as f:
				content = f.read()
			if lookup(content):
				w.write(filename + ': ' + content + '\n')


if __name__ == '__main__':
	main(sys.argv[1])