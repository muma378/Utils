# -*- coding: utf-8 -*-
import os
import json
import re

import pika
# import msg_filter
import msg2xlsx
from db import RecordManager
import settings

from jieba import posseg as pseg
from pyspark import SparkConf, SparkContext


# each rule stands for a conbination in the tuple
# such as ('t|m', 'v'), which indicates that 
# the line's tags were ought to contain 't' or 'm', then and 'v'
def rules_interpret(rule):
	syntax_parser = re.compile('.*'.join(rule))
	return lambda line: syntax_parser.search(line)

def word_segment(line):
	tags = [ tag for word, tag in pseg.cut(line) ]
	return (line, "".join(tags))

# TODO: look up the file to be processed in sqlite3
def target_files():
	return (os.path.join(settings.DATA_DIRECTORY, 'demo.txt'), 
		os.path.join(settings.SAVE_DIRECTORY, '12.txt'))

# TODO: run mutiple sc at one application
def filter_msgs(src_file, dst_file, category):
	valid_tags = rules_interpret(settings.SYNTAX_RULES[category])
	# TODO: rename app name for the project
	rdd = sc.textFile(src_file)
	valid_words = rdd.map(word_segment).filter(lambda pair: valid_tags(pair[1])).map(lambda x: x[0])
	
	valid_words.persist()
	valid_words.saveAsTextFile(dst_file)
	# return valid_words.collect()


def get_path(category):
	project_id = rm.last_record_id + 1
	
	last_source_file = rm.last_source
	try:
		file_index = re.match("^out_(?P<index>\d+)\.txt", last_source_file, re.UNICODE).group("index")
		file_index = int(file_index)
	except AttributeError, e:
		print "source file saved in the database is not legal"
		sys.exit(0)

	src_file = settings.SOURCE_FILE_TEMPLATE.format(index=file_index+1)
	print "file " + src_file + " will be used for project " + str(project_id)
	rm.insert_record(src_file, category)
	return src_file, project_id

def join_project_path(root_path, project_id):
	project_path = os.path.join(root_path, str(project_id))
	project_dir = os.path.dirname(project_path)
	if not os.path.exists(project_dir):
		os.makedirs(project_dir)
	return project_path


def convert_xlsx(temp_file, rows, category, project_id):

	partitions = msg2xlsx.smash_merged(temp_file, rows)
	if not msg2xlsx.is_valid(partitions, rows):
		print "rows in each partitions are not equal." 
	else:
		header = settings.XLSX_HEADERS[category]
		xlsx_path = join_project_path(settings.SAVE_DIRECTORY, project_id)

		last_end = rm.get_previous_end(project_id, category)
		retry_time = 0
		while not last_end: 
			sleep(60)	# waiting for next looking up
			retry_time += 1
			last_end = rm.get_previous_end(project_id, category)
			# TODO: use an alternative way to recover
			if retry_time > 10:
				print "unable to find an avaible value for %d" % project_id
				sys.exit(0)
			
		start = last_end + 1
		msg2xlsx.generate_xlsxs(partitions, header, xlsx_path, category, project_id, start)
		rm.update_record(project_id, start, start+len(partitions), rows)
	

def task_schedule(channel, method, header, body):
	print "received message: " + body
	channel.basic_ack(delivery_tag=method.delivery_tag)
	if header.content_type == "application/json":
		params = json.loads(body)
		try:
			if params.get("quit-spark") == True:
				channel.basic_cancel(consumer_tag="spark-consumer")
				channel.stop_consuming()
			else:
				category, rows = params["category"], params["rows"]
				filename, project_id = get_path(category)
				src_file = os.path.join(settings.DATA_DIRECTORY, filename)
				print "processing a request for " + category.encode('utf-8')
				temp_file = join_project_path(settings.TEMP_DIRECTORY, project_id)
				filter_msgs(src_file, temp_file, category)
				# convert text to xlsx
				convert_xlsx(temp_file, rows, category, project_id)

		except KeyError, e:
			print "params error, unable to call the application"
	else:
		print body
		print "illegal content type"


if __name__ == '__main__':
	rm = RecordManager()
	conf = SparkConf().setMaster(settings.MASTER_URL).setAppName(settings.APP_NAME)
	conf.setAll([("spark.eventLog.enabled", "true"), ("spark.eventLog.dir", settings.LOG_DIRECTORY)])
	# TODO:run several textfiles in parallel
	sc = SparkContext(conf=conf)

	credentials = pika.PlainCredentials(settings.RABBITMQ_USERNAME, settings.RABBITMQ_PASSWORD)
	conn_params = pika.ConnectionParameters(settings.RABBITMQ_HOST, credentials=credentials)
	conn_broker = pika.BlockingConnection(conn_params)
	# conn_broker = pika.BlockingConnection()

	channel = conn_broker.channel()

	channel.exchange_declare(exchange="spark-exchange",
							 type="direct",
							 passive=False,
							 durable=True,
							 auto_delete=False)

	channel.queue_declare(queue="spark-queue")

	channel.queue_bind(queue="spark-queue",
					   exchange="spark-exchange",
					   routing_key="msg-filter")

	channel.basic_consume(task_schedule, 
						  queue="spark-queue",
						  consumer_tag="spark-consumer")
	channel.start_consuming()