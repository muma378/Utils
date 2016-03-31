# -*- coding: utf-8 -*-
import os
import unittest
from mock import patch
from db import RecordManager

class RecordManagerTestCase(unittest.TestCase):
	def setUp(self):
		self.db_name = "test.db"
		if os.path.exists(self.db_name):
			os.remove(self.db_name)
		self.rm = RecordManager(self.db_name)

	def tearDown(self):
		# self.rm.conn.close()
		os.remove(self.db_name)

	def test_create_tables(self):
		self.rm.cursor.execute("select * from records")
		self.assertEqual(len(self.rm.cursor.fetchall()), 0)

	def test_insert_record(self):
		self.rm.insert_record('a.txt', u'地点', 111100, 111136, 100)
		self.rm.cursor.execute("select * from records")
		result = self.rm.cursor.fetchall()
		self.assertEqual(len(result), 1)
		self.assertEqual(result[0][3], 111100)
		self.rm.cursor.execute("select * from records where source=?", ('b.txt',))
		self.assertEqual(len(self.rm.cursor.fetchall()), 0)

		self.rm.insert_record('b.txt', u'日程', 100, 136, 50000)
		self.rm.cursor.execute("select * from records where source=?", ('b.txt',))
		result = self.rm.cursor.fetchall()
		self.assertEqual(len(result), 1)
		self.assertEqual(result[0][0], 2)

	def test_last_id(self):
		self.rm.cursor.execute("select * from records order by id")
		for i, row in enumerate(self.rm.cursor, start=1):
			self.assertEqual(row.id, i)
		
	def test_get_last_record(self):
		self.rm.insert_record('c.txt', u'日程', 137, 173, 5000)
		self.assertEqual(self.rm.get_last_record(u'日程')[1], 'c.txt')


	def test_update_record(self):
		self.rm.insert_record('d.txt', u'日程')
		pk = self.rm.last_record_id
		self.rm.update_record(pk, 100, 120, 1000)
		self.assertEqual(self.rm.get_last_record(u'日程')[3], 100)
		self.assertEqual(self.rm.get_last_record(u'日程')[5], 1000)

		self.rm.insert_record('c.txt', u'地点', 137, 173, 5000)
		pk = self.rm.last_record_id
		self.rm.update_record(pk, 100, 120, 1000)
		self.assertEqual(self.rm.get_last_record(u'地点')[3], 100)
