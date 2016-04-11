import os
import sys
import shutil

from audio import WaveWriter, WaveReader
from traverse import traverse

MAX_DURATION = 29 * 60
MAX_SIZE = 160 *1024 *1024	# bytes
# MAX_SIZE = 157286400
UNPORCESSED_LIST = "unprocess.txt"


def split_chunk(src_file, dst_file):
	print "processing " + src_file
	if os.stat(src_file).st_size > MAX_SIZE:
		record_fp.write(src_file + os.linesep)
		return

	wav = WaveReader(src_file)
	wav.lower_sampling(low_framerate=8000)
	# import pdb;pdb.set_trace()
	sections = wav.smart_truncate(MAX_DURATION)
	dirname = os.path.dirname(dst_file)
	if not os.path.exists(dirname):
		os.makedirs(dirname)
		
	if len(sections) == 1:
		WaveWriter(dst_file, wav.header, wav.content).write()
	else:
		for sec in sections:
			basename = os.path.basename(sec.filename)
			filename = os.path.join(dirname, basename)
			WaveWriter(filename, sec.header, sec.content).write()


if __name__ == '__main__':
	src_dir = sys.argv[1]
	dst_dir = sys.argv[2]
	record_fp = open(UNPORCESSED_LIST, 'a', 0)
	traverse(src_dir, dst_dir, split_chunk, target='.wav')
	# split_chunk(src_dir, dst_dir)