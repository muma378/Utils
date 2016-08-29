# QAmatcher.py - usage: python QAmatcher.py filename
# extracts questions and corresponding answers, 
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Aug.25

import re
import sys
from collections import OrderedDict
from common import parse
from common import utils

DECAY_FACTOR = 0.5

RANK_NAME_WITH_WEIGHT = "answers_rank_weight_{weight}.txt".format(weight=DECAY_FACTOR)

def regexp_interpretor(line, regexp):
	r = re.match(regexp, line, re.UNICODE)
	yield r.groups()

def counter_loader(ref, key, val):
	# accumulates the count for val 
	if ref.get(key):
		if not ref.get(key).get(val):
			ref[key][val] = 0
	else:
		ref[key] = {val:0}	

	ref[key][val] += 1
	return ref[key]


# qa_dict = {"question1": {"answer1":12, "answer2":23, "answer3":1}, ...}
def write_dict(d, q, out=sys.stdout, repeat=True):
	for k, v in d:
		# out.write(k + "\t" + str(v) + "\n")
		out.write("Q:{question}\tA:{answer}\tS:{score}\n".format(question=q, answer=k, score=v))
		if repeat:
			for i in xrange(v-1):
				out.write("Q:{question}\tA:{answer}\tS:{score}\n".format(question=q, answer=k, score=v))
		# out.write("Q:{question}\tA:{answer}\n".format(question=q, answer=k))

# evaluate the effect with differenet weights
def metric(d):
	pass


def display_dict(d):
	for k,v in d.items():
		print k,v

def sort_dict(frequency_dict, reverse=True):
	freqs = OrderedDict(sorted(frequency_dict.items(), key=lambda x: x[1], reverse=reverse))
	return freqs

def words_frequency_statistic(phrase_frequency):
	words_frequency = {}
	for phrase, frequency in phrase_frequency.items():
		words_list = utils.segment(phrase)
		for word in words_list:
			if not words_frequency.get(word):
				words_frequency[word] = 0
			words_frequency[word] = words_frequency[word]+1+(frequency-1)*DECAY_FACTOR

	# display_dict(sort_dict(words_frequency))

	# get weight for each phrase
	phrase_weight = {}
	for phrase in phrase_frequency.keys():
		words_list = utils.segment(phrase)
		weight = reduce(lambda x,y: x+words_frequency[y], words_list, 0)
		phrase_weight[phrase] = weight/len(words_list)

	# display_dict(sort_dict(phrase_weight))
	# import pdb;pdb.set_trace()
	return phrase_weight


def merge_dicts(od1, d2):
	for k, v in od1.items():
		pass


if __name__ == '__main__':
	filename = sys.argv[1]
	qa_regexp = r"[\w\\\.]*\s*Q ?:(.*)\s+A ?:(.*)$"
	interpretor = lambda x: regexp_interpretor(x.strip(), qa_regexp)
	loader = lambda d, k, v: parse.set_loader(d, k, v.strip())
	loader2 = lambda d, k, v: counter_loader(d, k, v.strip())

	qa_count_dict = parse.loads_dict(filename, interpretor, loader2)

	count_fp = open("answers_count.txt", "w")
	rank_fp = open(RANK_NAME_WITH_WEIGHT, "w")

	for question, answers in qa_count_dict.items():

		# count_fp.write("- " + question + ": \n" )
		# write_dict(sort_dict(answers), question, count_fp)

		rank_answers = words_frequency_statistic(answers)
		# rank_fp.write("- " + question + ": \n")
		sorted_rank_answers = sort_dict(rank_answers)


		junction_answers = [(k, answers[k]) for k, v in sorted_rank_answers.items()]

		write_dict(junction_answers, question, rank_fp, repeat=False)
