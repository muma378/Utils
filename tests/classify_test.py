# -*- coding: utf-8 -*-

import os
import unittest
import classify as cf

class ClassifyTestCase(unittest.TestCase):
	def setUp(self):
		self.test_info = """{"日期": "无", "文件名": "1 (100).jpg", "卡号类型": "浮凸", "平面卡号字体": "", "平面卡号颜色": "", "卡号板式": "19"}
{"日期": "无", "文件名": "1 (1017).jpg", "卡号类型": "浮凸", "平面卡号字体": "", "平面卡号颜色": "", "卡号板式": "19"}
{"日期": "有效日期", "文件名": "bankcard_1017967185.jpg", "卡号类型": "浮凸", "平面卡号字体": "", "平面卡号颜色": "", "卡号板式": "4-4-4-4"}
{"日期": "有效日期", "文件名": "bankcard_1017967372.jpg", "卡号类型": "浮凸", "平面卡号字体": "", "平面卡号颜色": "", "卡号板式": "4-4-4-4"}
"""
		

	def test_hashing(self):
		test_file = 'test_info.txt'
		with open(test_file, 'w') as f:
			f.write(self.test_info)

		hashed_info = cf.hashing(test_file)
		self.assertEqual(hashed_info[u"1 (100).jpg"][u"日期"], u"无")
		self.assertEqual(hashed_info[u"bankcard_1017967185.jpg"][u"日期"], u"有效日期")
		self.assertEqual(hashed_info[u"bankcard_1017967185.jpg"][u"卡号类型"], u"浮凸")
		os.remove(test_file)

	def test_traverse_dict(self):
		test_dirs = { 
			u"浮凸": {
				u"有日期": "", 
				u"无日期": ""}, 
			u"平面": {
				u"有日期": ""}
			}

		test_dirslist = [(u"浮凸",u"有日期"), (u"浮凸", u"无日期"), (u"平面", u"有日期")]
		test_dirslist = [ lambda x: os.path.join(*x), test_dirslist]

		for count, sub_dir in enumerate(cf.traverse_dict(test_dirs), start=1):
			self.assertTrue( sub_dir in test_dirslist )
		self.assertEqual(count, 3)
