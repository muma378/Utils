import os
import sys
import wave
from traverse import traverse
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

HEADER_SIZE = 44
WORKER_NUM = 4

# following settings shall be understood and written correctly
# audio settings
AS = {
	'header' : 44,
	'samplerate': 16000,
	'bitrate': 16,
	'channel': 1
}


# bitrate, samplerate are counted as bit
# body_size is counted as byte
def estimate(channels, bitrate, samplerate, body_size):
	return body_size*8.0/(channels*bitrate*samplerate)

def eval_wav_duration(wav_path):
	try:
		wr = wave.open(wav_path, 'rb')
		# nchannels, sampwidth(bytes), framerate, nframes, comptype, compname
		header = wr.getparams()
		# body_size = nframes * sampwidth
		# or 
		# os.stat(os.path.join(dirpath, filename)).st_size - HEADER_SIZE
		wr.close()
		return estimate(header[0], header[1]*8.0, header[2], header[3]*header[1])
	except Exception, e:
		print("Unable to read %s" % wav_path)
		return 0

# useless
# def eval_mp3_duration(mp3_path):
# 	try:
# 		body_size = os.stat(mp3_path).st_size - AS['header']
# 		return estimate(AS['channel'], AS['bitrate'], AS['samplerate'], body_size)
# 	except Exception, e:
# 		print("Unable to read %s" % mp3_path)
# 		return 0

def eval_dir(fn, files_list):
	pool = ThreadPool(WORKER_NUM)
	results = pool.map(fn, files_list)
	# close the pool and wait for the work to finish
	pool.close()
	pool.join()
	return sum(results)

files_list = []
def traverse_adaptor(src_dir, dst_dir):
	files_list.append(src_dir)

if __name__ == '__main__':
	src_dir = sys.argv[1]
	# files_list = [ os.path.join(src_dir, x) for x in os.listdir(src_dir) ]
	# print eval_dir(eval_wav_duration, files_list)
	traverse(src_dir, 'holder', traverse_adaptor)
	print eval_dir(eval_wav_duration, files_list)
