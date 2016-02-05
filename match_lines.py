# -*- coding: utf-8 -*-
import os
import sys
from sets import Set
import emotions

LANGUAGE = emotions.KR
HEADER = "Extracted Lines For {key}\n"

# unable to find the leaf finally
class AstaryException(Exception):
	pass

# translate the dict to a tree-like structure
# matched words are able to be found following the clues
def cultivate(corpus):
	tree = {}
	for key, words in corpus.items():
		for word in words:
			branching(tree, word, key)
	return tree

# add a branch for a word meanwhile the destination shall be the key(leaf)
def branching(tree, word, leaf):
	root = tree
	end = len(word)-1
	for i, char in enumerate(word):
		# given a leaf if it arrives at the end else a new brach
		root = root.setdefault(char, {} if i<end else {None: leaf})

# find a leaf according to the path(a generator for string)
def climb(tree, path):
	branch = tree
	try:
		for i, milestone in enumerate(path, start=1):
			branch = branch[milestone]
	except KeyError, e:
		if not branch.get(None):
			raise AstaryException('Unable to find the leaf.')
	# arrives at the end
	return branch[None]

# extracts lines matched the tree in to the dict extracted
def extract_matched(filename, tree, extracted):
	with open(filename, 'r') as f:
		for line in f:
			i = 0
			while i < len(line):
				if tree.get(line[i]):		# the entry
					try:
						key = climb(tree, line[i:])
						extracted.setdefault(key, Set()).add(line.strip())
						i += len(key)
					except AstaryException, e:
						i += 1
				else:
					i += 1
				
	return extracted

def write(filename, extracted):
	with open(filename, 'w') as f:
		for key, lines in extracted.items():
			f.write(HEADER.format(key=key.capitalize()))
			for line in lines:
				f.write(line+os.linesep)
			f.write("\n\n")
	print("Writes finished.")


def main():
	src_root = sys.argv[1]
	tree = cultivate(LANGUAGE)
	extracted = {}
	for filename in os.listdir(src_root):
		if filename.endswith('.txt'):
			extract_matched(os.path.join(src_root, filename), tree, extracted)
	dst_file = os.path.basename(src_root)
	write(dst_file+'.txt', extracted)


if __name__ == '__main__':
	main()