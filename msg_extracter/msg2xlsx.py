# -*- coding: utf-8 -*-
# msg2xlsx - usage: python msg2xlsx 
# transfer text in txt to xlsx
# author: liu size, xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.22
import os
import math
import time
from xlsx_handle import XlsxHandler
from db import RecordManager
import settings
from settings import logger

class ConvertingError(Exception):
	pass


def create_xlsx(lines, xlsx_name, header):
	xlsx = XlsxHandler()
	xlsx.create_excel(xlsx_name)
	xlsx.set_work_sheet({'bg_color': 'gray', 'sheet_long': 80, 'sheet_hight': 35})
	xlsx.set_excel_headers({'border': 6}, header)

	for i, line in enumerate(lines):
		xlsx.write_to_excel(i+2, 0, line.decode('utf-8'))
	xlsx.workbook.close()

def is_valid(partitions, rows):
	for p in partitions:
		if len(filter(lambda x: x.strip(), p)) != rows:
			return False
	return True

# xlsx_name_t = 'path/to/xlsx/日程27_%d.xlsx'
# call is_valid before this
def generate_xlsxs(partitions, header, xlsx_path, category, project_id, start):
	xlsx_name_t = get_name_template(xlsx_path, category, project_id, '.xlsx')
	for i, partition in enumerate(partitions):
		create_xlsx(partition, xlsx_name_t % (start+i), header)

def generate_txts(partitions, smash_path, category, project_id, start):
	txt_name_t = get_name_template(smash_path, category, project_id, '.txt')
	for i, partition in enumerate(partitions):
		with open(txt_name_t % (start+i), 'w') as f:
			f.write(os.newline.join(partition))	
	
def get_name_template(path, category, project_id, suffix):
	if not os.path.exists(path):
		os.mkdir(path)
	name_template = os.path.join(path, category+str(project_id)+"_%d"+suffix)
	return name_template


def smash_merged(merge_path, rows):
	# files were split into partitions after processing by spark
	filelist = filter(lambda x: x.startswith('part-'), os.listdir(merge_path))
	filelist = map(lambda x: os.path.join(merge_path, x), filelist)
	lines = []
	# concat before smashing
	for partition in filelist:
		with open(partition, 'r') as f:
			lines += filter(lambda x:x.strip(), f.read().split('\n'))
	partitions = [ lines[i:i+rows] for i in xrange(0, len(lines), rows) ]

	# removes the last row if it was not full
	if len(partitions[-1]) != len(partitions[0]):			
		return partitions[:-1]
	else:
		return partitions

def txt_2_xlsx(src_file, rows, category, project_id):
	rm = RecordManager()
	partitions = smash_merged(src_file, rows)
	if not is_valid(partitions, rows):
		logger.error("rows in each partitions are not equal.")
		raise ConvertingError
	else:
		header = settings.XLSX_HEADERS[category]
		xlsx_path = os.path.join(settings.SAVE_DIRECTORY, str(project_id))
		last_end = rm.get_previous_end(project_id, category)
		
		retry_time = 0
		while not last_end:
			logger.info("retriving value for last end failed, waiting for the next lookup")
			time.sleep(60)	# waiting for next looking up
			retry_time += 1
			last_end = rm.get_previous_end(project_id, category)
			# TODO: use an alternative way to recover
			if retry_time > 10:
				logger.error("unable to find an avaible value for %d" % project_id)
				raise ConvertingError
		start = last_end + 1
		generate_xlsxs(partitions, header, xlsx_path, category, project_id, start)
		rm.update_record(project_id, start, start+len(partitions), rows)
