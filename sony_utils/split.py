import os
import sys
import subprocess
import datetime

CMD_TEMPLATE = "cut.exe {src_wav} {dst_wav} {start} {end}"
NAME = "emotion_F_"
DECODING = 'gb2312' if os.name=='nt' else 'utf-8'

# split the wav as the information provided by several columns
def split_by_cols(cols_file, src_wav, dst_dir='.', name_prefix=NAME):
	with open(cols_file, 'r') as f:
		counter = 0
		for timeline in f:
			start, end, text = map(lambda x: x.strip(), timeline.split("\t"))
			
			to_sec = lambda x: str(float(x.split(":")[0])*60 + float(x.split(":")[1]))
			start, end = to_sec(start), to_sec(end)
			
			counter += 1
			
			dst_file = os.path.join(dst_dir, unicode(name_prefix+str(counter)))
			# to generate the wave
			dst_wav = dst_file + '.wav'
			cmd = CMD_TEMPLATE.format(**locals())
			subprocess.check_call(cmd, shell=True)

			# to generate the text
			with open(dst_file+".txt", "w") as t:
				t.write(text)

if __name__ == '__main__':
	split_by_cols(sys.argv[1], sys.argv[2])
