import os
import sys
import wave
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


def traverse(src_dir, dst_dir, fn, target='.wav'):
	for dirpath, dirnames, filenames in os.walk(src_dir):
		for filename in filenames:
			if filename.endswith(target):
				try:
					src_file = os.path.join(dirpath, filename)
					src_dir_len = len(src_dir) if src_dir.endswith(os.sep) else len(src_dir)+1
					dst_file = os.path.join(dst_dir, src_file[src_dir_len:])	# should not use replace
					fn(src_file, dst_file)
				except Exception as e:
					print e
					print("Unable to process %s" % src_file)

# bitrate, samplerate are counted as bit
# body_size is counted as byte
def estimate(channels, bitrate, samplerate, nframes):
	# return body_size*8.0/(channels*bitrate*samplerate)	# no need
	return nframes*1.0/samplerate		# nframes 

def eval_wav_duration(wav_path):
	try:
		wr = wave.open(wav_path, 'rb')
		# nchannels, sampwidth(bytes), framerate, nframes, comptype, compname
		# nframes that the lib gives are from data_size/samplewidth/nchannels
		# therefore, there is no need to consider channels when you want to estimate durations
		header = wr.getparams()
		# body_size = nframes * sampwidth
		# or 
		# os.stat(os.path.join(dirpath, filename)).st_size - HEADER_SIZE
		wr.close()
		return estimate(header[0], header[1]*8.0, header[2], header[3])
	except Exception, e:
		print("Unable to read %s" % wav_path)
		return 0

def eval_dir(fn, files_list):
	# for name in files_list:
	# 	print name, fn(name)
	# return reduce(lambda x, y: x+fn(y), files_list, 0)

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
