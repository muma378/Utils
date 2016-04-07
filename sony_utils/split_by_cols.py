import os
import sys
import subprocess
import datetime

CMD_TEMPLATE = "cut.exe {src} {dst} {start} {end}"
NAME = "emotion_F_"

def read_timeline(filename, src):
	with open(filename, 'r') as f:
		counter = 0
		for timeline in f:
			start, end, text = map(lambda x: x.strip(), timeline.split("\t"))
			
			to_sec = lambda x: str(float(x.split(":")[0])*60 + float(x.split(":")[1]))
			start, end = to_sec(start), to_sec(end)
			counter += 1
			dst = NAME + str(counter) + ".wav"
			cmd = CMD_TEMPLATE.format(**locals())
			subprocess.check_call(cmd, shell=True)

			with open(NAME+str(counter)+".txt", "w") as t:
				t.write(text)

if __name__ == '__main__':
	read_timeline(sys.argv[1], sys.argv[2])
