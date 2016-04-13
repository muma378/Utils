# -*- coding: utf-8 -*-
# pairwise.py - usage: import pairwise; pairwise.get_pairs(list1, list2, ...)
# util function to get pairs according to its similar names
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.April.12

import os
import distance
CACHE_FILENAME = 'pairs.cache'


def get_pairs(*lists, **options):
	pairs = options.get('pairs', [])
	method = options.get('method', 1)	# method 1 for shortest alignment, 2 for longgest
	# cache the result cause it is always time-consuming
	use_cache = options.get('use_cache', True)
	if use_cache and os.path.exists(CACHE_FILENAME):
			with open(CACHE_FILENAME, 'r') as f:
				cache = f.read().splitlines()
			for line in cache:
				pairs.append(filter(lambda x: x.strip(), map(lambda x: x.strip("' \""), line.split('***'))))
	else:
		for prime in lists[0]:
			pair = [ prime ]
			for minors in lists[1:]:
				# calculate its edit distance to the prime
				distances = map(lambda minor: distance.nlevenshtein(prime, minor, method), minors)
				# get the value whose levenshtein distance to the prime is the minimum
				most_matched = lambda l: minors[ l.index( min(l) ) ] 
				
				candidate = most_matched(distances)
				pair.append(candidate)
			pairs.append(pair)

		with open(CACHE_FILENAME, 'w') as f:
			for pair in pairs:
				f.write('***'.join(pair))	# write to files to cache
				f.write(os.linesep)

	return pairs

def exclude_same_pairs(*lists, **options):
	map_fns = options.get('map_fns', [lambda x: x, lambda x: x])
	if len(map_fns) != len(lists):
		print "number of lists is not equals to the map functions"
	pairs = options.get('pairs', [])
	to_delete = []
	for x in range(len(lists)):
		to_delete.append([])

	for pi, prime in enumerate(lists[0]):
		pair = []
		for mi, minors in enumerate(lists[1:], start=1):
			minor_key = map_fns[mi](prime)	#use corresponding mapping function
			try:
				minor_key_index = minors.index(minor_key)
			except ValueError, e:
				break		# must have the same elements in all lists
			else:
				to_delete[mi].append(minor_key_index)
				pair.append(minor_key)

		if pair:
			to_delete[0].append(pi)
			pair.insert(0, prime)
			pairs.append(pair)

	for li, deleted_indexs in enumerate(to_delete):
		deleted_indexs.sort(reverse=True)	# delete from the bottom to the top
		if len(deleted_indexs) > 1:
			assert(deleted_indexs[0] > deleted_indexs[1] )
		map(lambda i: lists[li].pop(i), deleted_indexs)
	return pairs