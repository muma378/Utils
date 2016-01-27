import os
import sys 
import Queue
import subprocess
import threading
from traverse import traverse, thread_traverse

CMD_TRUNCATE = 'wav.exe {src} {dst}'


class Truncator(threading.Thread):
	"""truncate wavs in the queue"""
	def __init__(self, src_queue):
		super(Truncator, self).__init__()
		self.src_queue = src_queue
		
	def run(self):
		while True:
			(src, dst) = self.src_queue.get()
			dst_dir = os.path.dirname(dst)
			if not os.path.exists(dst_dir):
				os.makedirs(dst_dir)
			cmd_truncate = CMD_TRUNCATE.format(**locals())
			try:
				os.popen(cmd_truncate)
			except Exception, e:
				print("Unable to process %s" % src)

			self.src_queue.task_done()


def truncate(src, dst):
	dst_dir = os.path.dirname(dst)
	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)
	cmd_truncate = CMD_TRUNCATE.format(**locals())
	os.popen(cmd_truncate)	

def main():
	src_dir = sys.argv[1]
	dst_dir = sys.argv[2]
	# traverse(src_dir, dst_dir, truncate, '.wav')
	thread_traverse(src_dir, dst_dir, Truncator, '.*\.wav')

if __name__ == '__main__':
	main()

	
