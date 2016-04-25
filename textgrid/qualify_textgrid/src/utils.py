# -*- coding: utf-8 -*-
import os
from datetime import datetime
import settings

# log name is composed by 3 parts: timestamp_type_basename.log
def get_log_path(log_type, target_path):
	timestamp = datetime.now().strftime(settings.LOG_DATETIME_FORMAT)
	basename = os.path.basename(target_path)
	log_name = settings.LOG_NAME_FORMAT.format(timestamp=timestamp, log_type=log_type, basename=basename)
	return os.path.join(settings.LOG_DIRECTORY_NAME, log_name)


# generator version for traversing
def traverser(src_dir, dst_dir, pattern):
	for dirpath, dirnames, filenames in os.walk(src_dir):
		for filename in filenames:
			if pattern.match(filename):
				try:
					src_file = os.path.join(dirpath, filename)
					src_dir_len = len(src_dir) if src_dir.endswith(os.sep) else len(src_dir)+1
					dst_file = os.path.join(dst_dir, src_file[src_dir_len:])	# should not use replace
					yield src_file, dst_file
				except Exception as e:
					logger.error(e)
					logger.error("unable to process %s" % src_file)


# intervals passed in ought to be sorted 
def get_layer(intervals, index=0):
	items = get_items(intervals)
	if index == 0:
		for item in items:
			yield item
	else:
		yield items[index-1]


def get_items(intervals):
	xmax = float('inf')
	items, item = [], []
	for interval in intervals:
		if xmax >= interval['xmax'] and interval['xmin'] == 0:	# value of xmax in the next layer must be less than or equals to the former one
			item = []
			items.append(item)

		item.append(interval)
		xmax = interval['xmax']
	return items

def flat_items(items): 	# makes neted items flatten
	intervals = []
	for item in items:
		intervals.extend(item)
	return intervals