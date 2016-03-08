import os
import sys
import subprocess
from parse_textgrid import TextgridParser

CMD_TEMPLATE = ('' if sys.platform=='win32' else './') + 'cut.exe "{src_file}" "{dst_file}" {start} {end}'

def split_layers(intervals):
	xmax = 0
	items = ([], [], [])
	layer_index = 0
	for interval in intervals:
		if xmax > interval['xmax']:
			layer_index += 1

		items[layer_index].append(interval)
		xmax = interval['xmax']
	return items

def split(items, audiofile):
	counter = 0
	for interval in items[0]:
		if interval['text'].startswith('1'):
			counter += 1
			dst_file = rename(items, counter, audiofile, interval)
			
			cmd = CMD_TEMPLATE.format(src_file=audiofile, dst_file=dst_file, start=interval['xmin'], end=interval['xmax'])
			subprocess.check_call(cmd, shell=True)
			with open(dst_file.replace('.wav', '.txt'), 'w') as f:
				f.write(interval['text'][1:])


def rename(items, index, filename, norm_interval):
	suffix = '.' + filename.split('.')[-1]
	name = filename[0:-len(suffix)]
	error = 0.1
	for interval in items[1]:
		if norm_interval['xmax'] <= interval['xmax']+error and norm_interval['xmin'] >= interval['xmin']-error:
			name += '_' + interval['text']
	for interval in items[2]:
		if norm_interval['xmax'] <= interval['xmax']+error and norm_interval['xmin'] >= interval['xmin']-error:
			if interval['text'] != '':
				name += '_' + interval['text']
	name += '_' + str(index) + suffix
	return name



if __name__ == '__main__':
	tp = TextgridParser()
	textfile = sys.argv[1]
	audiofile = sys.argv[2]
	tp.read(textfile)
	intervals = tp.parse_blocks()
	items = split_layers(intervals)

	split(items, audiofile)