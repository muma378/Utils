# add_noise.py - usage: python add_noise.py filename
# add a random (0~20) noise of 0.1s at the begining and ending of the original audio
import os
import sys
import wave
from struct import pack
from random import randrange

MAXVOLUME = 20


def waveproc(filename, dst_dir):
	wr = wave.open(filename, 'rb')
	# nchannels, sampwidth(bytes), framerate, nframes, comptype, compname
	header = list(wr.getparams())
	content = wr.readframes(header[3])
	
	noise_gen = noise_generator(header, 0.1, 2)
	header[3] += next(noise_gen)
	wr.close()

	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	import pdb;pdb.set_trace()
	# write frames
	ww = wave.open(os.path.join(dst_dir, filename), 'wb')
	ww.setparams(header)
	ww.writeframesraw(next(noise_gen))
	ww.writeframesraw(content)
	ww.writeframesraw(next(noise_gen))
	ww.close()

# duration counted as second
# num is how many pieces of noise to generate
def noise_generator(params, duration, num):
	nchannels, sampwidth, framerate = params[0:3]

	# the number of sampling between the duration
	sampling_size = int(duration * nchannels * framerate)
	# the size of noises generated in total
	yield num * sampling_size * sampwidth

	# identifiers for different size in lib struct
	packtype_map = { 
		1: 'c',
		2: 'h',
		4: 'l',
		8: 'q',
	}

	_type = packtype_map[sampwidth]
	for i in xrange(num):
		noise = [randrange(MAXVOLUME) for i in xrange(sampling_size)]
		yield pack(_type*sampling_size, *noise)

def readfiles(src_dir, dst_dir):
	for dirpath, dirnames, filenames in os.walk(src):
		for filename in filenames:
			try:
				import pdb;pdb.set_trace()
				child_dir = dirpath.replace(src_dir, '')
				waveproc(os.path.join(child_dir, filename), dst_dir)
			except Exception as e:
				print e
				print("Unable to process %s" % src_file)
	

def main():
	src = sys.argv[1]
	dst = sys.argv[2]
	length = 0.1

if __name__ == '__main__':
	main()