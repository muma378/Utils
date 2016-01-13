import os
import sys

def parse_line(line, names):
	columns = line.split('\t')
	if columns[1] == '1':
		url = unicode(columns[0], 'utf-8')
		try:
			groups = re.search(URL_PATTERN, url, re.UNICODE).groupdict()
			info = {'slice': int(groups['slice']), 'xmin': str(float(groups['start'])+float(columns[2])), 'xmax': str(float(groups['start'])+float(columns[3])), 'text': columns[4]}
		except (AttributeError, ValueError) as e:
			if columns[2] == 'None':
				columns[2] = 0
				info = {'slice': int(groups['slice']), 'xmin': str(float(groups['start'])+float(columns[2])), 'xmax': str(float(groups['start'])+float(columns[3])), 'text': columns[4]}
				print("Warning: the start time for %s is None" % columns[0])
			else:
				print "Unable to parse the url: " + url
				return
		names.append(groups['name'])

def readfiles(root_dir):
	names = []
	for file in os.listdir(root_dir):
		if file.endswith('.txt'):
			with open(file, 'r') as f:
				for line in f:
					parse_line(line, names)
			with open(file.replace('.txt', 'names.txt'), 'w') as f:
				for name in names:
					f.write(name)

if __name__ == '__main__':
	readfiles(sys.argv[0])
