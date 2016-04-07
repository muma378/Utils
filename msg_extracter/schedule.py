# -*- coding: utf-8 -*-
import os
import re
import json
import shutil

import pika
from jieba import posseg as pseg
from pyspark import SparkConf, SparkContext

import application
import msg2xlsx
import settings
from db import RecordManager
from settings import logger


def create_project(category):
	rm = RecordManager()
	project_id, last_source = rm.last_record_id+1, rm.last_source
	logger.info("creating a project for category: " + category.encode('utf-8'))
	try:
		file_index = re.match(settings.FILE_INDEX_PATTERN, last_source, re.UNICODE).group(1)
		src_file = settings.SOURCE_FILE_TEMPLATE.format(index=int(file_index)+1)
	except AttributeError, e:
		logger.error("source file saved in the database is not legal")
		raise e
	logger.info("file %s will be used for project %d" % (src_file, project_id))
	rm.insert_record(src_file, category)
	return src_file, project_id

def clean(project_id, dirs=()):
	rm = RecordManager()
	rm.delete_record(project_id)

	for path in dirs:
		try:
			shutil.rmtree(path)
		except OSError, e:
			continue

def task_schedule(channel, method, header, body):
	logger.info("received message: " + body)
	if header.content_type == "application/json":
		params = json.loads(body)
		if params.get(settings.RABBITMQ_MSG_QUIT) == True:
			# quit the queue
			channel.basic_ack(delivery_tag=method.delivery_tag)
			channel.basic_cancel(consumer_tag=settings.RABBITMQ_SPARK['consumer-tag'])
			channel.stop_consuming()

		else:
			try:
				category, rows = params["category"], params["rows"]
			except KeyError, e:
				logger.error("params error, unable to call the application")
				return
			
			filename, project_id = create_project(category)
			src_file = os.path.join(settings.DATA_DIRECTORY, filename)
			temp_file = os.path.join(settings.TEMP_DIRECTORY, str(project_id))
			try:
				# procsessing with application
				application.filter_msgs(sc, src_file, temp_file, category)
			except Exception, e: # TODO
				logger.error("filtering failed, clean the previous work")
				clean(project_id, dirs=[temp_file, ])
				return

			try:
				# convert text to xlsx
				msg2xlsx.txt_2_xlsx(temp_file, rows, category, project_id)
			except msg2xlsx.ConvertingError:
				logger.error("converting failed, clean the previous work")
				xlsx_path = os.path.join(settings.SAVE_DIRECTORY, project_id)
				clean(project_id, dirs=[temp_file, xlsx_path])
				return
				
			# processed ack
			channel.basic_ack(delivery_tag=method.delivery_tag)
	else:
		logger.error("illegal content-type: " + header.content_type)


if __name__ == '__main__':
	# initialize spark
	conf = SparkConf().setMaster(settings.SPARK_MASTER_URL).setAppName(settings.SPARK_APP_NAME)
	conf.setAll([("spark.eventLog.enabled", "true"), ("spark.eventLog.dir", settings.LOG_DIRECTORY)])
	sc = SparkContext(conf=conf)

	# initialize rabbitmq
	credentials = pika.PlainCredentials(settings.RABBITMQ_CONN_CONF['username'], settings.RABBITMQ_CONN_CONF['password'])
	conn_params = pika.ConnectionParameters(settings.RABBITMQ_CONN_CONF['host'], credentials=credentials)
	conn_broker = pika.BlockingConnection(conn_params)

	channel = conn_broker.channel()
	channel.exchange_declare(exchange=settings.RABBITMQ_SPARK['exchange'],
							 type="direct",
							 passive=False,
							 durable=True,
							 auto_delete=False)

	channel.queue_declare(queue=settings.RABBITMQ_SPARK['queue'])
	channel.queue_bind(queue=settings.RABBITMQ_SPARK['queue'],
					   exchange=settings.RABBITMQ_SPARK['exchange'],
					   routing_key=settings.RABBITMQ_SPARK['routing-key'])

	channel.basic_consume(task_schedule, 
						  queue=settings.RABBITMQ_SPARK['queue'],
						  consumer_tag=settings.RABBITMQ_SPARK['consumer-tag'])
	channel.start_consuming()