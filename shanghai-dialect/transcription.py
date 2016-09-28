# transcript.py - usage: python transcript.py ref.dict root
# translate each line for all text file under root directory
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Sep.05

import os
import sys
from common.parse import loads_dict, chars_interpretor, simple_interpretor
from common.traverse import traverser
from common.utils import spell_sentence


def spell(root_dir, ref):
	for src_file, dst_file in traverser(root_dir, "transcription", ".txt"):
		with open(src_file, 'r') as f:
			dst_dir_path = os.path.dirname(dst_file)
			if not os.path.isdir(dst_dir_path):
				os.makedirs(dst_dir_path)
			with open(dst_file, 'w') as w:
 				for line in f:
 					sentence = line.strip().split('\t')[-1]
 					trans = spell_sentence(sentence, ref)
 					w.write("{0}\t{1}\n".format(line.strip(), trans))


if __name__ == '__main__':
	ref_file = sys.argv[1]
	root_dir = sys.argv[2]
	ref = loads_dict(ref_file, simple_interpretor)
	spell(root_dir, ref)
