# -*- coding: utf-8 -*-
import os
import sys
import re
from datetime import datetime
from dp.core.base.traverse import traverser
from dp.core.base.load import load_xlsx, dump_xlsx

import simhash

def record_validator(record, col_num, predicate):
	try:
		return predicate(record[col_num])
	except AttributeError as e:
		print "an error raised but ignored when for {0}".format(e)
		return False	

def validator_factory(col_num, predicate, err_msg):
	
	def validator(record, lineno):
		try:
			if predicate(record[col_num]):
				return True
			else:
				print "row {0} was removed for {1}".format(lineno, err_msg)
				return False
		except AttributeError as e:
			print "an error raised but ignored at lineno {0} for {1}".format(lineno, e)
			return False

	return validator

def find_col_num(row, title):
	try:
		return row.index(title)
	except ValueError as e:
		for i, t in enumerate(row):
			print("{0}.{1}".format(i, t.encode("utf-8")))
		col_num = raw_input("no matched title for {0} was found, please enter the correct number:\n".format(title.encode('utf-8')))
		return int(col_num)

def sheet_with_lineno(sheet, start=1):
	return zip(sheet, range(start+1, len(sheet)+2))


def cleaner_factory(col_num, prog, repl):
	def sub_all(record):
		text = record[0][col_num]
		while(prog.search(text)):
			# print text.encode('utf-8')
			text = prog.sub(repl, text)
		record[0][col_num] = text
		return record
	return sub_all

def str_from_time(record, col_num):
	record[0][col_num] = record[0][col_num].strftime("%y/%m/%d")
	return record



def process_sheet(sheet, start=1):
	titles, content = sheet[0], sheet[start:]
	# filters
	date_validate = validator_factory(find_col_num(titles, u"发布时间"), lambda cell: cell.year > 2014, "invalidate date")
	length_validate = validator_factory(find_col_num(titles, u"正文"), lambda cell: len(cell) > 100, "too short content")
	clean_sheet = filter(lambda x: date_validate(x[0], x[1]) and length_validate(x[0], x[1]),  sheet_with_lineno(content))

	# removes unnecessary symbols
	quot_prog = re.compile("(.*)&quot(.+?)&quot(.*)", re.UNICODE)
	quot_repl = u"\g<1>“"+"\g<2>"+u"”\g<3>"
	title_quote_cleaner = cleaner_factory(find_col_num(titles, u"标题"), quot_prog, quot_repl)
	clean_sheet = map(title_quote_cleaner, clean_sheet)

	date_col = find_col_num(titles, u"发布时间")
	clean_sheet = map(lambda x: str_from_time(x, date_col), clean_sheet)

	text_col_no = find_col_num(titles, u"正文")
	simhash_objects = []
	for row, lineno in clean_sheet:
		if len(row) > text_col_no:
			# print row[text_col_no].encode("utf-8")
			so = simhash.SimhashObject(row[text_col_no], label=lineno)
			simhash_objects.append(so)

	near_dup_set = set()
	for i, so1 in enumerate(simhash_objects):
		if i == len(simhash_objects):
			break
		for so2 in simhash_objects[i+1:]:
			similarity = so1.cosine_sim(so2)
			if similarity > 0.8:
				print "{0} & {1}: {2}".format(so1.label, so2.label, similarity)
				near_dup_set.add(so2.label)

			# distance = so1.hamming_dist(so2)
			# if distance < 3:
			# 	print "{0} & {1}: {2}".format(so1.label, so2.label, distance)

	print near_dup_set
	unique_sheet = filter(lambda x: x[1] not in near_dup_set, clean_sheet)
	content = zip(*unique_sheet)[0]	# remove list for lineno	
	sheet = [titles]
	sheet.extend(content)
	return sheet

if __name__ == '__main__':
	dirname = sys.argv[1]
	destname = sys.argv[2]
	for src_file, dest_file in traverser(dirname, destname, target='.xlsx'):
		if os.path.basename(src_file).startswith('~'):	# temp files for xlsx
			continue

		print("processing {0} ...".format(src_file))		
		workbook = load_xlsx(src_file)
		for title, sheet in workbook.items():
			workbook[title] = process_sheet(sheet)

		dump_xlsx(workbook, dest_file)