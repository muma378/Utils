import sys

class BaseEvaluator(object):
	"""base class to provide an template for derived classes"""
	def __init__(self):
		super(BaseEvaluator, self).__init__()
	
	# process intervals and return self
	def evaluate(self, intervals):
		raise NotImplementedError

	def output(self, fd=sys.stdout):
		raise NotImplementedError 	#fd.write('')