import re
import os
import sys


SUBRULES = (
	(re.compile("^1"), ""),
	(re.compile("\"\""), "\""),
	(re.compile("(\S)\["), "\g<1> ["),
	)

def sub(content):
	for parser, repl in SUBRULES:
		content = parser.sub(repl, content)
	return content

def main(target):
	files = filter(lambda x: x.endswith(".txt"), os.listdir(target))
	for filename in files:
		with open(filename, 'r') as f:
			content = f.read()
		with open(filename, 'w') as f:
			f.write(sub(content))


if __name__ == '__main__':
	main(sys.argv[1])