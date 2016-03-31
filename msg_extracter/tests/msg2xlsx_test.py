# -*- coding: utf-8 -*-
import os
import shutil
import unittest
from mock import patch
import msg2xlsx

class Msg2xlsxTestCase(unittest.TestCase):
	def setUp(self):
		self.data1 = """济微路十字路口济南大学西门［或者七贤广场］即可…
今晚我存342。上存2579。加起来我存2920。
来了三天，今下午就回去了
旅馆。不是咱俩在一起的地方。"""
		self.data2 = """麻烦收件，九五同城速递，
妹，我今晚给周厅长饯行，明早回匀
你爸刚才自己开车回去了"""
		self.data3 = ""
		
		self.test_dir = 'data'
		if os.path.exists(self.test_dir):
			shutil.rmtree(self.test_dir)
		os.mkdir(self.test_dir)

		data_list = [self.data1, self.data2, self.data3]
		self.test_list = []
		for i, data in enumerate(data_list):
			filename = os.path.join(self.test_dir, 'part-'+str(i))
			with open(filename, 'w') as f:
				f.write(data)
			self.test_list.append(filename)
		self.result = msg2xlsx.smash_merged('./data', 3)


	def tearDown(self):
		shutil.rmtree(self.test_dir)
		# for test_file in self.test_list:
		# 	os.remove(test_file)

	def test_smash_merged(self):
		self.assertEqual(len(self.result), 2)
		self.assertEqual(len(self.result[0]), 3)
		self.assertEqual(len(self.result[1]), 3)
		
	def test_is_valid(self):
		self.assertTrue(msg2xlsx.is_valid(self.result, 3))
		self.assertTrue(msg2xlsx.is_valid(self.result[:-1], 3))

	def test_generate_xlsxs(self):
		header = [['A1:A2',u"语料",80],
            ['B1:B2',u"所有具体地点", 25],
            ['C1:C2',u"所有具体最长地点", 25],
            ['D1:D2',u"所有细化地点", 25],
            ['E1:E2',u"细化地点类型", 25],
            ['F1:F2',u"标注疑惑备注", 25],
        ]
		msg2xlsx.generate_xlsxs(self.result, header, 'data/test', u'地点', 2, 100)
		suppose_to_gen = [u'地点2_100.xlsx', u'地点2_101.xlsx']

		filelist = map( lambda x: x.decode('utf-8'), os.listdir('data/test'))
		self.assertEqual(len(filelist), 2)
		for filename in filelist:
			self.assertTrue(filename in suppose_to_gen)

	def test_name_template(self):
		test_dir = 'data/test_dir'
		self.assertEqual(msg2xlsx.get_name_template(test_dir, u'日程', 27, '.xlsx'), u'data/test_dir/日程27_%d.xlsx')
		self.assertTrue(os.path.isdir(test_dir))
		shutil.rmtree(test_dir)
