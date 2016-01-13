# add_noise.py - usage: python add_noise.py src_dir dst_dir
# add a random (0~20) noise of 0.1s at the begining and ending of the original audio
import os
import sys
import wave
from struct import pack
from random import randrange

MAXVOLUME = 20
MEDIA = '.wav'

def waveproc(src_file, dst_file):
	wr = wave.open(src_file, 'rb')
	# nchannels, sampwidth(bytes), framerate, nframes, comptype, compname
	header = list(wr.getparams())
	content = wr.readframes(header[3])
	
	noise_gen = noise_generator(header, 0.1, 2)
	header[3] += next(noise_gen)
	wr.close()

	dst_dir = os.path.dirname(dst_file)
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)

	# write frames
	ww = wave.open(dst_file, 'wb')
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

	packendian_map = {
		'little': '<',
		'big':'>',
	}

	_type = packtype_map[sampwidth]
	for i in xrange(num):
		noise = [randrange(MAXVOLUME) for i in xrange(sampling_size)]
		yield pack(packendian_map[sys.byteorder]+_type*sampling_size, *noise)


def readfiles(src_dir, dst_dir):
	for dirpath, dirnames, filenames in os.walk(src_dir):
		for filename in filenames:
			if filename.endswith(MEDIA):
				try:
					src_file = os.path.join(dirpath, filename)
					dst_file = os.path.join(dst_dir, src_file[len(src_dir):])	# should not use replace
					waveproc(src_file, dst_file)
				except Exception as e:
					print e
					print("Unable to process %s" % src_file)
		

def main():
	src = sys.argv[1]
	dst = sys.argv[2]
	readfiles(src, dst)


if __name__ == '__main__':
	main()