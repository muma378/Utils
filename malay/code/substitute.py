import re
import os
import sys


SUBRULES_0 = (
	(re.compile("^1"), ""),
	(re.compile("\"\""), "\""),
	(re.compile("(\S)\["), "\g<1> ["),
	(re.compile("\](\S)"), "] \g<1>"),
	)

SUBRULES_ASTRO = (
	(re.compile("\[diaorang\]"), "{diaorang}"),
	(re.compile("\[(#brg|3brt)\]"), "[#brt]"),
	(re.compile("\[Albeni_Petron\]"), "{Albeni_Petron}"),
	(re.compile("{spain}"), "{Spain}"),
	(re.compile("{DuDu}"), "{dudu}"),
	)

SUBRULES_ASTRO_2 = (
	(re.compile("\{diaorang\}"), "diaorang"),
	(re.compile("\[(aiya|membawakan \[aa)\]"), "??"),
	(re.compile("\[hehe\]"), "[#grb]"),
	)

SUBRULES_INEWS = (
	(re.compile("\[fiskau\]"), "??"),
	(re.compile("\[Indonesia\]"), "Indonesia"),
	)

SUBRULES_TV3 = (
	(re.compile("{oh aktifnya}"), "oh aktifnya"),
	(re.compile("\[yeah\]"), "yeah\""),
	)

SUBRULES_TV3_2 = (
	(re.compile("\[dah\]"), "dah"),
	)

def sub(content):
	for parser, repl in SUBRULES:
		content = parser.sub(repl, content)
	return content

def main(target):
	files = filter(lambda x: x.endswith(".txt"), os.listdir(target))
	for filename in files:
		filename = os.path.join(target, filename)
		with open(filename, 'r') as f:
			content = f.read()
		with open(filename, 'w') as f:
			f.write(sub(content))


if __name__ == '__main__':
	main(sys.argv[1])