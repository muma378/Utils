# -*- coding: utf-8 -*-
# dialect.py - usage: python dialect.py dict.txt content.txt
# segments sentence and annotates word with phonetic marks
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Jun.03

import os
import re
import sys
import jieba

single_word_file = "single_word_dic.txt"
single_char_file = "single_char_dic.txt"

punctuation = ['，', '。', '？', '！', '：', '；', '《', '》', '、', '’', '”', '“', 
	'［', '］', '（', '）', '．', ':', ',', '.', '?', '!', '…', '—', '(', ')', '=', ]

# item displayed in dict is like the below:
# 国 kueq	美 mhe1	
# 国 kueq	米 mij2	
# 国 kueq	民 min4	
# 国 kueq	民 min4	党 taon3	
# 国 kueq	民 min4	革 chij4\keq	命 min4	
def loads_dict(dict_file):
	phonetic_dict = {}
	with open(dict_file, 'r') as f:
		for line in f:
			items = re.split('\t| ', line)
			word, phonetic = separate(items)
			phonetic_dict[word] = phonetic

	return phonetic_dict

# usually, items are word and phonetic interleaved
# ['国', 'kueq',	 '民', 'min4']
def separate(items):
	word, phonetic = '', ''
	for item in items:
		try:
			if item:
				phonetic += item.decode('ascii') + ' '
		except UnicodeDecodeError, e:
			word += item
	return word, phonetic.strip()


# content is dispalyed as below:
# data\G3229\wav\943900_1622_3229_S0214.txt	[s]亮剑 每日播放几集
# data\G3229\wav\943900_1622_3229_S0215.txt	[t][s]我讲了 侬听到了没有[t]
# data\G3229\wav\943900_1622_3229_S0216.txt	[s]下趟侬就是男生了
def spell(content_file, phonetic_dict):
	mute_words = set()
	with open(single_word_file, 'w') as fw:
		with open(content_file, 'r') as fr:
			for line in fr:
				sentences = line.split('\t')
				if len(sentences) != 2:
					print line
					continue
				
				for word in segment(clean(sentences[1])):
					word = word.encode('utf-8')
					if phonetic_dict.get(word):
						fw.write(word)
						fw.write('\t' + phonetic_dict[word] + '\n')
					else:
						if word.strip() not in punctuation:
							mute_words.add(word)
		for word in mute_words:
			fw.write(word)
			fw.write('\n')


def spell_each(content_file, phonetic_dict):
	mute_chars = set()
	with open(single_char_file, 'w') as fw:
		with open(content_file, 'r') as fr:
			for line in fr:
				sentences = line.split('\t')
				if len(sentences) != 2:
					print line
					continue
				
				for word in segment(clean(sentences[1])):
					encoded_word = word.encode('utf-8')
					if phonetic_dict.get(encoded_word):
						phonetic = phonetic_dict[encoded_word].split(' ')
						for i, character in enumerate(word):
							fw.write(character.encode('utf-8'))
							fw.write('\t' + phonetic[i] + '\n')
					else:
						if encoded_word.strip() not in punctuation:
							mute_chars.update(list(word))
		for character in mute_chars:
			fw.write(character.encode('utf-8'))
			fw.write('\n')


def segment(line):
	seg_list = jieba.cut(line, cut_all=False)
	return filter(lambda x: x.strip(), seg_list)


# removes all [s], [t] and letters wrapped with []
def clean(line):
	return re.sub("\[.\]", '', line)


if __name__ == '__main__':
	dict_file = sys.argv[1]
	content_file = sys.argv[2]
	phonetic_dict = loads_dict(dict_file)
	spell(content_file, phonetic_dict)
	spell_each(content_file, phonetic_dict)

