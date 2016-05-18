# log.py - a flyweight class to provide same interfaces for logging lib
import os

class LogHandler(object):
	"""docstring for LogHandler"""
	def __init__(self, filename, stdout=False):
		super(LogHandler, self).__init__()
		self.filename = filename
		self.stdout = stdout
		self.fp = open(filename, 'a', 0)

	def __del__(self):
		self.fp.close()

	def error(self, msg):
		self.fp.write('error: ' + msg + os.linesep)
		if self.stdout:
			print('error: ' + msg)

	def info(self, msg):
		self.fp.write(msg + os.linesep)
		if self.stdout:
			print(msg)

