import os
import re
import threading
import Queue

WORKER_NUM = 1

class Traverser(threading.Thread):
	"""
		traverses all dirs under the queue of dir,
		generates a queue of pair tuple including src_file and dst_file

	"""
	def __init__(self, dir_queue, out_queue, root_dir, dst_dir, filter_pattern='.*\.wav'):
		super(Traverser, self).__init__()
		self.dir_queue = dir_queue
		self.out_queue = out_queue
		self.dst_dir = dst_dir
		self.root_dir = root_dir
		self.filter = re.compile(filter_pattern, re.UNICODE)

	def run(self):
		while True:
			src_dir = self.dir_queue.get()

			items = os.listdir(src_dir)
			for item in items:
				full_path = os.path.join(src_dir, item)
				if os.path.isdir(full_path):
					self.dir_queue.put(full_path)
				elif self.filter.match(full_path):
					# extract the dst path
					root_dir_len = len(self.root_dir ) if src_dir.endswith(os.sep) else len(self.root_dir )+1
					dst_file = os.path.join(self.dst_dir, full_path[root_dir_len:])	# should not use replace

					self.out_queue.put((full_path, dst_file))

			self.dir_queue.task_done()


def thread_traverse(src_dir, dst_dir, thread_class, pattern='.*\.wav'):
	src_queue = Queue.Queue()
	out_queue = Queue.Queue()

	for i in range(WORKER_NUM):
		producer = Traverser(src_queue, out_queue, src_dir, dst_dir, pattern)
		producer.setDaemon(True)
		producer.start()

	# root dir
	src_queue.put(src_dir)

	for i in range(WORKER_NUM):
		consumer = thread_class(out_queue)
		consumer.setDaemon(True)
		consumer.start()

	src_queue.join()
	out_queue.join()


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

def traverse_with_extra(src_dir, dst_dir, fn, target='.wav', **extra_args):
	for dirpath, dirnames, filenames in os.walk(src_dir):
		for filename in filenames:
			if filename.endswith(target):
				try:
					src_file = os.path.join(dirpath, filename)
					src_dir_len = len(src_dir) if src_dir.endswith(os.sep) else len(src_dir)+1
					dst_file = os.path.join(dst_dir, src_file[src_dir_len:])	# should not use replace
					fn(src_file, dst_file, **extra_args)
				except Exception as e:
					print e
					print("Unable to process %s" % src_file)