import os
import sys
import shutil
from traverse import traverse


RENAMES_LIST = "renamed.txt"

def slot_in(src_file, _):
	filename = os.path.basename(src_file)
	slots.setdefault(filename, []).append(src_file)

def rename_duplicated(slots, dst_dir):
	for basename, locations in slots.items():
		if len(locations) > 1:	# duplicated names
			for location in locations:
				parent_dir = os.path.basename(os.path.dirname(location))
				dst_file = os.path.join(dst_dir, parent_dir + '_' + basename)
				record_fp.write("rename " + location + " to " + dst_file + '\n')
				shutil.copy(location, dst_file)
		else:
			dst_file = os.path.join(dst_dir, basename)
			shutil.copy(locations[0], dst_file)

if __name__ == '__main__':
	slots = {}
	src_dir = sys.argv[1]
	dst_dir = sys.argv[2]
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)
		
	record_fp = open(RENAMES_LIST, 'a', 0)
	traverse(src_dir, "", slot_in, target='.wav')
	rename_duplicated(slots, dst_dir)
