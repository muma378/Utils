# -*- coding: utf-8 -*-
import os
import sys
import re
import chardet
import shutil
from traverse import traverse

# sub_parser = re.compile('^([\s\w]+?\.pcm\s*\n)+', re.MULTILINE)
blank_parser = (re.compile('^.*\.pcm\s*\n', re.MULTILINE), '')	# remove line with pcm and empty ones

subnum_parser = re.compile('(sp)(\d+)(_\w+\.pcm)')

def backup(src_file, suffix='.bak'):
	shutil.copy(src_file, src_file+suffix)

# remove lines with pcm names and insert correct names into the first line
def insert(src_file, pcm_files):
	with open(src_file, 'rb') as f:
		raw_data = f.read()
		coding = chardet.detect(raw_data)['encoding']
		data = raw_data.decode(coding)
		clean_data = blank_parser[0].sub(blank_parser[1], data)

	with open(src_file, 'w') as f:
		f.write(pcm_files.encode('utf-8'))
		f.write(clean_data.encode('utf-8'))
		print("write %s to %s" % (pcm_files.strip(), src_file))

# replace each name.pcm with correct_index_name.pcm
def replace(src_file, pcm_files):
	index = re.search('sp(\d+).lable.txt', src_file).group(1)
	with open(src_file, 'rb') as f:
		raw_data = f.read()
		coding = chardet.detect(raw_data)['encoding']
		data = raw_data.decode(coding)
		clean_data = subnum_parser.sub('\g<1>'+index+'\g<3>', data)


	with open(src_file, 'w') as f:
		f.write(clean_data.encode('utf-8'))

		print("write %s to %s" % (pcm_files.strip(), src_file))


def adapter(src_file, _):
	if os.path.basename(src_file).startswith('.!'):
		return 

	_dir = os.path.dirname(src_file)
	pcm_files = ('\t').join(filter(lambda x: x.endswith('.pcm'), os.listdir(_dir))) + os.linesep

	backup(src_file)
	insert(src_file, pcm_files)
	# replace(src_file, pcm_files)


def main():
	root_dir = sys.argv[1]
	traverse(root_dir, '', adapter, '.txt')


if __name__ == '__main__':
	main()