# -*- coding: utf-8 -*-
import hashlib
from math import sqrt
import jieba.analyse

class SimhashObject(object):
	"""a document was taken and a hash object was returned"""
	def __init__(self, doc, label=None):
		super(SimhashObject, self).__init__()
		self.doc = doc
		self.label = label
		self._tokenize()
		self._hash()
		
	def _tokenize(self, topK=20):
		self.tokens_with_weight = jieba.analyse.extract_tags(self.doc, topK=topK, withWeight=True)
		return self.tokens_with_weight

	# width deciedes how many bits was kept 
	# and need to be longer than hash_fn's block size
	def _hash(self, hash_fn=hashlib.md5, width=128):

		def token_sign(token, weight):
			hexstr = hash_fn(token).hexdigest()
			binstr = bin(int(hexstr, 16))[2:].zfill(width)	# get the binary representation
			sign = map(lambda x: (int(x)-0.5)*weight, list(binstr))	# flip the weight if the bit was zero
			return sign

		def list_add(list1, list2):
			"""
			add corresponding elements in each list
			"""
			assert len(list1) == len(list2)
			return map(lambda x: x[0]+x[1], zip(list1, list2))


		signs = map(lambda x: token_sign(x[0].encode('utf-8'), x[1]), self.tokens_with_weight)	# get hash sign for each token
		fingerprint = reduce(lambda x, y: list_add(x, y), signs)	# add each bit in all signs
		self.fp_bits = map(lambda x: 1 if x > 0 else 0, fingerprint)
		self.fingerprint = ''.join(map(lambda x: str(x), self.fp_bits))
		return self.fingerprint

	# for its speciality (only including 0 and 1), 
	# its cosine value (Va*Vb/(|Va|*|Vb|)) can be computed in a trick way
	def cosine_sim(self, that):
		fp_dot = map(lambda x: x[0] * x[1], zip(self.fp_bits, that.fp_bits))	# get its bit_and
		
		count = lambda l: len(filter(lambda x: x, l))

		numerator = count(fp_dot)
		denominator = sqrt(count(self.fp_bits)*count(that.fp_bits))

		assert denominator != 0
		return numerator/denominator


	def hamming_dist(self, that):
		fp_dot = map(lambda x: 1 if x[0]!=x[1] else 0, zip(self.fp_bits, that.fp_bits))	# xor
		return len(filter(lambda x: x, fp_dot))
		



		