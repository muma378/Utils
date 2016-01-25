# truncate_wav.py - usage: python truncate_wav.py src_dir dst_dir settings
# truncate wavs as the settings indicates
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.01.18

import os
import sys
import subprocess
import shutil

MEDIA = '.wav'
START = 'hdTimeStart'
END = 'hdTimeEnd'
FILENAME = 'file'
CMD_TEMPLATE = './cut.exe {src_file} {dst_file} {start} {end}'

def parse_settings(filename):
	settings = {}
	with open(filename) as f:
		for line in f:
			d = eval(line)
			settings[d[FILENAME]] = {'start': d[START], 'end':d[END]}
	return settings

def wavcut(src_file, dst_file, setting):
	setting['src_file'] = src_file
	setting['dst_file'] = dst_file

	cmd = CMD_TEMPLATE.format(**setting)
	subprocess.check_call(cmd, shell=True)

def readfiles(src_dir, dst_dir, settings_file):
	settings = parse_settings(settings_file)
	for dirpath, dirnames, filenames in os.walk(src_dir):
		for filename in filenames:
			src_file = os.path.join(dirpath, filename)
			src_dir_len = len(src_dir) if src_dir.endswith(os.sep) else len(src_dir)+1
			dst_file = os.path.join(dst_dir, src_file[src_dir_len:])	# should not use replace
		
			dst_child = os.path.dirname(dst_file)
			if not os.path.exists(dst_child):
				os.makedirs(dst_child)

			if filename.endswith(MEDIA):
				try:
					setting = settings[filename]
					wavcut(src_file, dst_file, setting)
				except Exception as e:
					print e
					print("Unable to process %s" % src_file)
			else:
				shutil.copy(src_file, dst_file)

if __name__ == '__main__':
	readfiles(sys.argv[1], sys.argv[2], sys.argv[3])