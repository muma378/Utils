import os
import re
import sys
import shutil


NAME_INDEX_PARSER = re.compile("\w+_(?P<index>\d+)\.\w{3}$")

def main(target, start):
	names = filter(lambda x: x.endswith((".txt", ".wav")), os.listdir(target))
	for name in names:
		r = NAME_INDEX_PARSER.match(name)
		if r:
			index = str(int(r.group('index'))+int(start))
			rolling_name = re.sub('^(\w+_)\d+\.(\w{3})$', '\g<1>'+index+'\g<2>', name)
			shutil.move(os.path.join(target, name), os.path.join(target, rolling_name))
		else:
			raise ValueError	

if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2])