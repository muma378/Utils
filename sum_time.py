import os
import sys

def main(filename):
	added = 0
	original = 0
	with open(filename) as f:
		f.readline()
		for line in f:
			l = line.split('\t')
			original += float(l[1])
			added += float(l[2])
	print("time added: %s, time in total: %s" % (added, original)) 

if __name__ == '__main__':
	main(sys.argv[1])