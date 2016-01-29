#!/usr/bin/python
# -*- coding: utf-8 -*-
# db_handler.py - provides uniform interfaces to query or modify the database
# authors: Liu Size, Xiao Yang<xiaoyang0117@gmail.com>
# date: 2016.01.28

import sys
import time
import random
import logging
import pymssql
from settings import sqlserver_settings as s
from settings import logger

MAX_INTERVAL = 500

class SQLServerHandler(object):
	"""an instance to query and modify data in the sqlserver"""
	def __init__(self):
		super(SQLServerHandler, self).__init__()
		self.conn = self.__connect()
		self.cursor = self.conn.cursor()

	def __del__(self):
		self.conn.close()

	def __connect(self):
		conn_cnt = 0
		logger.info('trying to connect to sqlserver on %s:%s' % (s.get('host'), s.get('port')))
		while conn_cnt < s.get('reconnect_cnt', 3):
			try:
				conn = pymssql.connect(host=s.get('host'), port=s.get('port'), user=s.get('user'),\
					password=s.get('password'), database=s.get('database'), charset=s.get('charset'))
				return conn
			except Exception, e:	# add a specified exception
				conn_cnt += 1
				logger.debug('connecting failed, times to reconnect: %d' % conn_cnt)
		
		logger.warning('unable to establish a connection, waiting for the next time')
	
	# TODO: increase intervals if connecting failed to many times
	def connect(self):
		while not self.conn:
			self.conn = self.__connect()
			if not self.conn:
				interval = random.randint(0, s.get('reconnect_interval', MAX_INTERVAL))
				logger.info('connection will be established in %ss' % interval)
				time.sleep(interval)

	def exec_query(self, sql_query):
		if not sql_query:
			logger.warn('sql error')
			return
		if not self.conn:
			self.conn = self.connect()
			self.cursor = self.conn.cursor()
		
		try:
			logger.info('executes sql: "%s"' % sql_query)
			self.cursor.execute(sql_query)
			result = self.cursor.fetchall()
		except Exception as e:
			logger.error(e)
			return

		if result:
			logger.info('quering executed successfully')
		else:
			logger.info('quering executed with no result')
		return result

	# to add, delete and modify
	def exec_commit(self, sql):
		if not sql:
			logger.error("sql error")
			return
		if not self.conn:
			self.conn = self.connect()
			self.cursor = self.conn.cursor()

		try:
			logger.info('executes sql: %s' % sql_query)
			self.cursor.execute(sql)
			self.cursor.commit()
		except Exception as e:
			logger.error(e)
			return 
		
		logger.info('sql executed successfully')

	#TODO: execute many at one time
	def exec_many(self, sql, arg):
		raise NotImplementedError