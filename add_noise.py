# add_noise.py - usage: python add_noise.py src_dir dst_dir
# add a random (0~20) noise of 0.1s at the begining and ending of the original audio
import os
import sys
import wave
from math import pow, sqrt
from struct import pack, unpack
from random import randrange, gauss

MAXVOLUME = 20
MEDIA = '.wav'
# the length of orignial audio to be sampled
SAMPLE_LEN = 0.3
# the length of noise to be added
NOISE_LEN = 0.1 # to be a variable

THRESHOLD = 30


PACKTYPE_MAP = { 
	1: 'c',
	2: 'h',
	4: 'l',
	8: 'q',
}

PACKENDIAN_MAP = {
	'little': '<',
	'big':'>',
}


def waveproc(header, content):
	samples = extract_samples(header, SAMPLE_LEN, content)
	noise_gen = noise_generator(header, NOISE_LEN, 2, samples)
	header[3] += next(noise_gen)
	return noise_gen

def waveio(src_file, dst_file):
	wr = wave.open(src_file, 'rb')
	# nchannels, sampwidth(bytes), framerate, nframes, comptype, compname
	header = list(wr.getparams())
	content = wr.readframes(header[3])
	wr.close()

	noise_gen = waveproc(header, content)	

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

def threshold_wav(samples):
	 for sample in samples:
	 	if gauss_params(sample)[1] < THRESHOLD:
	 		yield True
	 	else:
	 		yield False
	 	

# extracts a piece of sample respectively at the begining and ending
def extract_samples(params, duration, content):
	nchannels, sampwidth, framerate = params[0:3]
	nframes = int(duration * nchannels * framerate)
	nbytes = nframes *  sampwidth

	positions = [(0, nbytes), (-nbytes, None)]
	fmt = PACKENDIAN_MAP[sys.byteorder] + PACKTYPE_MAP[sampwidth]*nframes
	return unpack_samples(fmt, content, positions)

def unpack_samples(fmt, content, positions):
	samples = []
	for start, end in positions:
		samples.append(unpack(fmt, content[start:end]))
	return samples

# duration counted as second
# num is how many pieces of noise to generate
def noise_generator(params, duration, num, samples):
	nchannels, sampwidth, framerate = params[0:3]
	# the number of frames between the duration
	sampling_size = int(duration * nchannels * framerate)
	# the size of noises generated in total
	yield num * sampling_size * sampwidth

	_endian = PACKENDIAN_MAP[sys.byteorder]
	# identifiers for different size in lib struct
	_type = PACKTYPE_MAP[sampwidth]
	for i in xrange(num):
		mu, sigma = gauss_params(samples[i])
		# noise = [randrange(MAXVOLUME) for i in xrange(sampling_size)]
		noise = [gauss(mu, sigma) for i in xrange(sampling_size)]
		yield pack(_endian+_type*sampling_size, *noise)

def mean(l):
	return sum(l)/len(l)

# unbiased estimitor for sample standard deviation
# N-1 instead of N
def stddev(l, mu):
	return sqrt(sum([ pow(i-mu, 2) for i in l ])/(len(l) - 1))

def gauss_params(l):
	N = len(l)
	# mean
	mu = sum(l) / N
	# sample standard deviation
	sigma = sqrt(sum([ pow(i-mu, 2) for i in l ])/(N - 1))
	return mu, sigma


def readfiles(src_dir, dst_dir):
	for dirpath, dirnames, filenames in os.walk(src_dir):
		for filename in filenames:
			if filename.endswith(MEDIA):
				try:
					src_file = os.path.join(dirpath, filename)
					dst_file = os.path.join(dst_dir, src_file[len(src_dir):])	# should not use replace
					waveio(src_file, dst_file)
				except Exception as e:
					print e
					print("Unable to process %s" % src_file)
		

def main():
	src = sys.argv[1]
	dst = sys.argv[2]
	readfiles(src, dst)


if __name__ == '__main__':
	main()