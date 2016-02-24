# -*- coding: utf-8 -*-
# merge_index.py - usage: python merge_index.py dir1 dir2 ... ref.xlsx 
# merge files in root_dirs with similar names, and sort as the order of text listed in ref.xlsx
# author: Xiaoyang <xiaoyang0117@gmail.com>
# date: 2016.02.23
import os
import sys
import re
import shutil
import openpyxl as px
import distance


NAME_IN_COMMON_PARSER = re.compile('(?P<common_part>\w+)_\d')
normalize_dir = lambda x: x.strip().lower() 

normalize_key = lambda x: x.replace(' ', '').encode('utf-8')

def parse_xlsx(ref_xlsx, sheet):
	wb = px.load_workbook(filename=ref_xlsx, read_only=True)
	ws = wb[sheet]

	index_parser = re.compile('.*_(?P<index>\d+)')
	index = {}
	for row in ws.rows:
		try:
			# name = int(index_parser.match(row[0].value).group('index'))
			name = int(row[0].value)
			# strip the string and encode with default coding to do hashing
			index.setdefault(normalize_key(row[1].value), []).append(name)
		except (AttributeError, TypeError), e:
			# attribute error for unmatched row
			# type error for blank row
			if row[0].value or row[1].value:
				print('Uable to parse %s' % row[0].value)

	return index

# find directories with similar/same names and put them in a set
# to merge them later
def group_similar_dir(dirs):
	group = {}
	for root_dir in dirs:
		sub_dirs = os.listdir(root_dir)
		for dir_name in sub_dirs:
			abs_path = os.path.join(root_dir, dir_name)
			if os.path.isdir(abs_path):
				group.setdefault(normalize_dir(dir_name), []).append(abs_path)
	return group 


# dig until no folders inside
def dig_dirs(_dir):
	leaf_dirs = []
	for dirpath, dirnames, _ in os.walk(_dir):
		if not dirnames:
			leaf_dirs.append(os.path.join(dirpath))
	return leaf_dirs


def get_similar(seq, dismatched, max_norm_distance=0.5):
	measured = [ distance.nlevenshtein(seq, line[0], method=2) for line in dismatched ]
	if measured and min(measured) < max_norm_distance:
		return dismatched.pop(measured.index(min(measured)))
	else:
		return None


# merge files in the same set listed in dir_groups
# besides, rename and sort it according to ref and identifier
def merge_sort(dir_group, ref, identifier, dst_dir):
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	homo_wav = lambda x: x.replace('.txt', '.wav')	# find the corresponding wav file
	mark = '<' + identifier[0].upper() + '>'

	# to reuse later
	# remeber to pop the index not assign
	def mv(key, src_path, index):
		if not ref[key]:
			ref.pop(key) # remove the item if no values contained
		
		basename = identifier + '_' + str(index) + '.txt'
		dst_path = os.path.join(dst_dir, basename)

		shutil.copy(src_path, dst_path)
		shutil.copy(homo_wav(src_path), homo_wav(dst_path))


	dismatched = []
	for _dir in dir_group:
		for leaf_dir in dig_dirs(_dir):	# get the leaf dirs
			textfiles = filter(lambda x: x.endswith('.txt'), os.listdir(leaf_dir))
			for textfile in textfiles:
				abs_path = os.path.join(leaf_dir, textfile)
				with open(abs_path, 'r') as f:
					try:
						# strip marks and spaces
						key = f.read().replace(mark, '').replace(' ', '').strip()
						mv(key, abs_path, ref[key].pop(0))
					
					# text may be incomplete, save them to find the similar later
					except KeyError, e:
						dismatched.append((key, abs_path))
			
	# try to find the similar ones (dismatched for carelessness)
	for seq, indexes in ref.items():
		count = len(indexes)
		while count:
			count -= 1
			similar = get_similar(seq, dismatched)
			if similar:
				_, src_path = similar
				mv(seq, src_path, indexes.pop(0))

	if ref:
		f.write('***********'+identifier+':'+str(dir_group)+"***********\n")
		with open('diff.txt', 'a') as f:
			f.write(">>dirs not listed in excel:\n")
			f.write(str(dismatched))
			f.write("\n>>text listed but not existed:\n")				
			f.write(str(ref))
			f.write("\n\n\n")

def main():
	dirs = sys.argv[2:-1]
	dst_dir = sys.argv[-1]
	ref_xlsx = sys.argv[1]

	groups = group_similar_dir(dirs)

	for key, dir_group in groups.items():
		order_ref = parse_xlsx(ref_xlsx, key)
		dst_sub_dir = os.path.join(dst_dir, key.capitalize(), key)
		merge_sort(dir_group, order_ref, key, dst_sub_dir)



if __name__ == '__main__':
	main()