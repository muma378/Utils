# -*- coding: utf-8 -*-
# flatten_dirs.py - usage: python flatten_dirs.py root_dir
# extract files in all subdirectories and flat them in order, (while highlight files containing marks)
# author: Xiaoyang <xiaoyang0117@gmail.com>
# date: 2016.02.23
import os
import sys
import re
import shutil

# Owl1-300_1_4.418_10.820.txt
NAME_PATTERN = '^(?P<identity>[a-zA-Z]+)(?P<start>\d+)-\d+_(?P<index>\d+)_?[0-9._]*\.(?P<type>(txt)|(wav))$'
name_parser = re.compile(NAME_PATTERN)
# Owl_1.txt
rename = lambda r: r.group('identity')+'_'+str(int(r.group('start'))+int(r.group('index'))-1)+'.'+r.group('type')

def validate(src_root):
	# TODO: to validate if the number of files in each dir is correct
	pass

def flatten(src_file, dst_file):
	global name_parser
	basename = os.path.basename(src_file)
	r = name_parser.match(basename)
	if r:
		dst_file = os.path.join(os.path.dirname(dst_file), rename(r))
		shutil.copy(src_file, dst_file)
	else:
		print('Unabel to match %s' % basename)

# to rename files if <O>(<E>, <D> etc.) existed in the text
def highlight(flatten_dir):
	print "highlighting the text and wav with specified marks..."
	texts = filter(lambda x: x.endswith('.txt'), os.listdir(flatten_dir))
	homo_wav = lambda x: x.replace('.txt', '.wav')	# find the corresponding wav file

	for t in texts:
		mark = t[0].upper()
		sign = '<' + mark + '>'
		abs_path = os.path.join(flatten_dir, t)
		with open(abs_path, 'r') as f:
			if f.read().find(sign) != -1:
				new_name = os.path.join(flatten_dir, t.replace('_', '_'+mark+'_'))
				shutil.move(abs_path, new_name)
				shutil.move(homo_wav(abs_path), homo_wav(new_name))


def traverse(src_dir, dst_dir, fn, target='.wav'):
	print("flattening files in %s to %s..." % (src_dir, dst_dir)) 
	for dirpath, dirnames, filenames in os.walk(src_dir):
		for filename in filenames:
			if filename.endswith(target):
				try:
					src_file = os.path.join(dirpath, filename)
					dst_file = os.path.join(dst_dir, filename)	
					fn(src_file, dst_file)
				except Exception as e:
					print e
					print("Unable to process %s" % src_file)

def main():
	src_root = sys.argv[1]
	dst_root = os.path.join(src_root, 'flatten')
	if not os.path.exists(dst_root):
		os.makedirs(dst_root)
	traverse(src_root, dst_root, flatten, target='')
	highlight(dst_root)

if __name__ == '__main__':
	main()
