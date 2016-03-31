# -*- coding: utf-8 -*-
import sys
import sqlite3
from datetime import datetime

import settings

class RecordManager(object):
	def __init__(self, db_name=settings.DATABASE_NAME):
		super(RecordManager, self).__init__()
		self.conn = sqlite3.connect(db_name)
		self.cursor = self.conn.cursor()
		self.time_format = "%Y-%m-%d %H:%M"

	def __del__(self):
		self.conn.close()

	@property
	def last_record_id(self):
		_last_id = self.last('id', 'records')
		return _last_id[0] if _last_id else 0

	@property
	def last_source(self):
		_last_source = self.last('source', 'records')
		if _last_source:
			return _last_source[0]
		else:
			print "please specify the last source in database"
			sys.exit(0)

	def last(self, field, table):
		self.cursor.execute("""SELECT %s FROM %s ORDER BY id DESC""" % (field, table))
		return self.cursor.fetchone()

	def create_tables(self):
		# id also stands for project id
		self.cursor.execute('''CREATE TABLE records 
			(id INTEGER PRIMARY KEY ASC,
			 source TEXT UNIQUE, 
			 category TEXT NOT NULL, 
			 start INTEGER, 
			 end INTEGER, 
			 rows INTEGER, 
			 date TEXT)''')
		
		# status: start => filtering => filtered => assemble => end
		# self.cursor.execute('''CREATE TABLE orders 
		# 	(id integer, source text, status text, rows integer, category text)''')
		self.conn.commit()

	def insert_record(self, source, category, start=None, end=None, rows=None, pk=None):
		if id:
			new_id = pk
		else:
			new_id = self.last_record_id + 1

		record = (new_id, source, category, start, end, rows, datetime.now().strftime(self.time_format))
		self.cursor.execute("""INSERT INTO records VALUES
			(?, ?, ?, ?, ?, ?, ?)
			""", record)
		self.conn.commit()

	def update_record(self, pk, start, end, rows):
		self.cursor.execute("""UPDATE records SET start=?, end=?, rows=? WHERE id=?
			""", (start, end, rows, pk))
		self.conn.commit()

	def get_last_record(self, category):
		self.cursor.execute("""SELECT * FROM records WHERE category=? ORDER BY id DESC
			""", (category,))
		return self.cursor.fetchone()

	def get_previous_end(self, pk, category):
		self.cursor.execute("""SELECT * FROM records WHERE category=? ORDER BY id DESC
			""", (category,))

		# looking for a previous record according to pk
		results = self.cursor.fetchall()
		assert(len(results) != 0)
		try:
			for i, item in enumerate(results):
				if item[0] == pk:
					end = results[i+1][4]	# end
					break
		except IndexError, e:
			end = 0
		return end

if __name__ == '__main__':
	# run once to initialize the database
	rm = RecordManager()
	try:
		rm.create_tables()
	except sqlite3.OperationalError, e:
		print "tables created already"

	rm.insert_record('out_1.txt', u'地点', start=100, end=300, rows=100, pk=3)
	rm.insert_record('out_2.txt', u'日程', start=500, end=530, rows=1000, pk=4)

