# disassemble_json.py - usage: python disassemble_json.py filename.json
# a temporary script to work with batch_imgproc.sh and cvutils.
# it is for the situation that all pixels to marks are stored in a json file instead of 
# corresponding path to a text file. 
# with running the script, it is able to generate the directories and text file,
# which makes it possible to call the batch_imgproc.sh directly
import os
import sys

BOX_TEMPLATE = "{0},{1}\t{2},{3}\t-1,-1\n"
POINT_TEMPLATE = "-1,-1\t-1,-1\t{0},{1}\n"
ROOT_DIR = 'Position/'

def readjson(filename):
	with open(filename, 'r') as f:
		for line in f:
			pos_dict = eval(line)
			disassemble(pos_dict)

def disassemble(pos_dict):
	pos_file = (ROOT_DIR + pos_dict['picture'] + '.txt').replace("\\", '/')
	
	d = os.path.dirname(pos_file)
	if not os.path.exists(d):
		os.makedirs(d)

	with open(pos_file, 'w') as f:
		for pos in pos_dict['data']:
			box = pos['box']
			f.write(BOX_TEMPLATE.format(box['x'], box['y'], box['x']+box['w'], box['y']+box['h']))
			for p in pos['points']:
				f.write(POINT_TEMPLATE.format(p['x'], p['y']))

if __name__ == '__main__':
	readjson(sys.argv[1])