import os
import sys
import shutil
import subprocess
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


def cpp_split_chunk(src_file, dst_file, online_file):
	print "processing " + src_file
	dirname = os.path.dirname(dst_file)
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	import pdb;pdb.set_trace()
	online_dir = os.path.dirname(online_file)
	if not os.path.exists(online_dir):
		os.makedirs(online_dir)
	try:
		subprocess.check_call(["audio.exe", src_file, dst_file, online_file])
	except subprocess.CalledProcessError, e:
		record_fp.write(src_file + "with error " + e + os.linesep)
		raise Exception


def traverse_with_3(src_dir, dst_dir, fn, target='.wav'):
	for dirpath, dirnames, filenames in os.walk(src_dir):
		for filename in filenames:
			if filename.endswith(target):
				try:
					src_file = os.path.join(dirpath, filename)
					src_dir_len = len(src_dir) if src_dir.endswith(os.sep) else len(src_dir)+1
					dst_file = os.path.join(dst_dir, src_file[src_dir_len:])	# should not use replace
					online_file = os.path.join(dst_dir, '8K', src_file[src_dir_len:])
					fn(src_file, dst_file, online_file)
				except Exception as e:
					print e
					print("Unable to process %s" % src_file)

if __name__ == '__main__':
	src_dir = sys.argv[1]
	dst_dir = sys.argv[2]
	record_fp = open(UNPORCESSED_LIST, 'a', 0)
	traverse_with_3(src_dir, dst_dir, cpp_split_chunk, target='.wav')
	# traverse(src_dir, dst_dir, split_chunk, target='.wav')
	# split_chunk(src_dir, dst_dir)
