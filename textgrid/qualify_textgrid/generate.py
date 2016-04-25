# -*- coding: utf-8 -*-
import os
import utils
import settings
from settings import logger

class TextgridGenerator(object):
	"""to generate a textgird with intervals passed in"""
	
	TEMPLATE_HEADER = u"""File type = "ooTextFile"
Object class = "TextGrid"

xmin = {global_xmin}
xmax = {global_xmax}
tiers? <exists>
size = {items_size}
item []:
"""

	TEMPLATE_ITEM = u"""	item [{item_index}]:
		class = "{class}"
		name = "{name}"
		xmin = {xmin}
		xmax = {xmax}
		intervals: size = {size}
"""

	TEMPLATE_INTERVALS = u"""			intervals [{slice}]:
			xmin = {xmin}
			xmax = {xmax}
			text = "{text}"
"""

	def __init__(self):
		super(TextgridGenerator, self).__init__()

	def __write_header(self, fd, **kwargs):
		fd.write(TextgridGenerator.TEMPLATE_HEADER.format(**kwargs).encode(settings.ENCODING))

	def __write_item(self, fd, **kwargs):
		fd.write(TextgridGenerator.TEMPLATE_ITEM.format(**kwargs).encode(settings.ENCODING))

	def __write_interval(self, fd, **kwargs):
		fd.write(TextgridGenerator.TEMPLATE_INTERVALS.format(**kwargs).encode(settings.ENCODING))
	
	def write(self, fd, items_info, intervals):
		items = utils.get_items(intervals)
		self.__write_header(fd, global_xmin=intervals[0][settings.INTERVAL_KEY_XMIN], 
			global_xmax=intervals[-1][settings.INTERVAL_KEY_XMAX], items_size=len(items))
		for i, item_info in enumerate(items_info, start=0):
			self.__write_item(fd, **item_info)
			for interval in items[i]:
				self.__write_interval(fd, **interval)