# list_all.py - usage: python list_all.py root_dir
# choose the directory which contains a bunch of text with specified name, 
# then extract all text into a file named list_all.txt
# author: Xiaoyang <xiaoyang0117@gmail.com>
# date: 2016.02.05

import os
import sys
import re
import shutil

LISTTXT_NAME = 'list_all.txt'
NAMEPATTERN = '([a-zA-Z_<>]*)(?P<index>\d+)(\.txt)'
INDEX_PARSER = re.compile(NAMEPATTERN)

homo_wav = lambda x: x.replace('.txt', '.wav')	# find the corresponding wav file
move = lambda x, y: shutil.move(x, y) or shutil.move(homo_wav(x), homo_wav(y))	# shutil.move returns None always

def extract_text(abs_path, textfiles):
	print "extracting text to %s" % LISTTXT_NAME
	brother_dir = os.path.dirname(abs_path)
	listall_txt = os.path.join(brother_dir, LISTTXT_NAME)
	parent_dir = './' + os.path.basename(abs_path)
	with open(listall_txt, 'w') as f:
		textfiles = filter(lambda x: INDEX_PARSER.match(x), textfiles)
		textfiles.sort(key=lambda x: int(INDEX_PARSER.match(x).group('index')))
			
		
		for filename in textfiles:
			with open(os.path.join(abs_path, filename)) as tf:
				f.write(parent_dir+'/'+filename+os.linesep)
				f.write(tf.read().strip()+os.linesep)


def rotate_names(abs_path, textfiles):
	print "rotating files..."
	textfiles.sort(key=lambda x: int(INDEX_PARSER.match(x).group('index')))
	rotated_textfiles = []
	for i, filename in enumerate(textfiles, start=1):
		rotated_name = INDEX_PARSER.sub('\g<1>%d\g<3>'%i, filename)
		move(os.path.join(abs_path, filename), os.path.join(abs_path, rotated_name))
		rotated_textfiles.append(rotated_name)
	return rotated_textfiles

# to rename files if <O>(<E>, <D> etc.) existed in the text
def highlight(abs_path, textfiles):
	print "highlighting the text and wav with specified marks..."
	highlighted = []
	for filename in textfiles:
		mark = filename[0].upper()
		sign = '<' + mark + '>'
		src_file = os.path.join(abs_path, filename)
		with open(src_file, 'r') as f:
			if f.read().find(sign) != -1:
				filename = filename.replace('_', '_'+mark+'_')
				move(src_file, os.path.join(abs_path, filename))
			highlighted.append(filename)
	return highlighted

def select_dir(src_dir, *fns):
	dirs = [src_dir]
	while len(dirs) != 0:
		_dir = dirs.pop()
		dirs += filter(os.path.isdir, map(lambda x: os.path.join(_dir, x), os.listdir(_dir)))
		textfiles = filter(lambda x: x.endswith('.txt') and INDEX_PARSER.match(x), os.listdir(_dir))
		if len(textfiles) > 0:
			print 'processing %s ...' % _dir
			for fn in fns:
				if textfiles:
					textfiles = fn(_dir, textfiles)
				else:
					print 'program ends at %s' % fn.__str__()
					break

def main():
	fns = (rotate_names, highlight, extract_text)
	select_dir(sys.argv[1], *fns)

if __name__ == '__main__':
	main()