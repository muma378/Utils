import sys

def load_file(subset_file):
	allocated = {}
	with open(subset_file) as f:
		for line in f:
			line = line.strip()
			if line:
				allocated[line] = 1
	return allocated

if __name__ == '__main__':
	filename = sys.argv[1]
	allocated = load_file(filename)
	with open(filename) as f:
		for line in allocated.keys():
			f.write(line)