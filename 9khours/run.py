import os
import sys

import subprocess

DECODING = 'gb2312'
ENCODING = 'utf-8'


def traverse(src_dir, target='.wav'):
	filelist = []
	for dirpath, dirnames, filenames in os.walk(src_dir):
		targets = filter(lambda x: x.endswith(target), filenames)
		filelist.append(map(lambda x: os.path.join(dirpath, x).decode(DECODING), targets))
	
	return filelist

def dumps(filelist, name='temp.txt'):
	with open(name, 'w') as f:
		for filename in filelist:
			f.write(filename.encode(CODING))
	return name


target = sys.argv[1]
filelist = traverse(target)
filelist_name = dumps(filelist)
# split big chunk into the proper
subprocess.check_call(["CheckLength2hr.exe", filelist_name])

filelist = traverse(target)
dest = sys.argv[2]
for filename in filelist:
	subproccc.check_call()
