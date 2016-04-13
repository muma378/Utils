# -*- coding: utf-8 -*-
import os
import sys
import json
import shutil

from collections import OrderedDict

TEXTINFO_KEY = u"文本级信息"
CHARINFO_KEY = u"字符级信息"

LINENO = 0

INCORRECT_NUMS = 0

def loads(info_txt):
	info_list = []
	global LINENO
	with open(info_txt,'r') as f:
		for line in f:
			LINENO += 1
			info = json.loads(line)
			info_list.append(sort(info))
	return info_list

# unzip list composed of dict
def flat(dict_list):
	ordered = []
	for d in dict_list:
		for k, v in d.items():
			ordered.append((k, v))
	return ordered 


def sort(info):
	global INCORRECT_NUMS
	text_infos = info.pop(TEXTINFO_KEY)
	card_num = match_text(text_infos, lambda k: len(k)>=12, 'card number')	# guess it stood for date
	valid_date = match_text(text_infos, lambda k: u"/" in k, 'valid date')	# guess it was valid date
	ordered_append(info, TEXTINFO_KEY, (card_num, valid_date, text_infos))	

	char_infos = info.pop(CHARINFO_KEY)
	card_chars = match_chars(char_infos, card_num)
	date_chars = match_chars(char_infos, valid_date)
	if card_num:
		if len(card_chars) == 0:
			for key in card_num.keys():
				INCORRECT_NUMS += 1
				print "unable to find chars for card number: " + key
	else:
		print info[u"文件名"]

	ordered_append(info, CHARINFO_KEY, (card_chars, date_chars, char_infos))
	return info


# append each field as required
def ordered_append(info, key, ordered_infos):
	for ordered_info in ordered_infos[:-1]:
		if ordered_info:
			if type(ordered_info) == list:
				info.setdefault(key, []).extend(ordered_info)
			else:
				info.setdefault(key, []).append(ordered_info)
		
	if ordered_infos[-1]:
		info.setdefault(key, []).extend(ordered_infos[-1])
	return info

# uses boolean function to extract(guess) fields
def match_text(text_infos, is_valid, name):
	global LINENO
	for i, text_info in enumerate(text_infos):
		for key in text_info.keys():
			if is_valid(key):	
				return text_infos.pop(i)
	# print "unable to extract " + name + " in line" + str(LINENO)
	return None

# use text_info extracted before to match corresponding characters
def match_chars(char_infos, text_info):
	matched = []
	if text_info:
		for key in text_info.keys():
			text_info_str = key
		for i, char_info in enumerate(char_infos):
			for key in char_info.keys():
				if text_info_str.startswith(key):
					matched = char_infos[i:i+len(text_info_str)]
					if is_same(text_info_str, matched):
						char_infos = char_infos[:i] + char_infos[i+len(text_info_str):]		# remove the slice 
						return matched
	return []

# make sure if it was extracted correctly
def is_same(nums, dict_list):
	for i, d in enumerate(dict_list):
		for key in d.keys():
			if not nums[i] == key:
				return False
	return True


def dumps(info_list, info_txt):
	with open(info_txt, 'w') as f:
		for info in info_list:
			f.write(json.dumps(info, ensure_ascii=False).encode('utf-8'))
			f.write('\n')



if __name__ == '__main__':
	info_txt = sys.argv[1]
	dst_file = sys.argv[2]
	info_list = loads(info_txt)
	dumps(info_list, dst_file)
	print str(INCORRECT_NUMS)
