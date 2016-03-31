import os
import sys
import re
import json
import yaml
import pika
import settings

def read_yaml(invoice_file):
	return yaml.load(file(invoice_file, 'r'))

def interpret(invoice_file):
	invoice = read_yaml(invoice_file)
	for product in invoice['products']:
		for index in range(product['quantity']):
			params = {'category':product['category'], 'rows':product['rows']}
			publish(params)

# params need: src_file, dst_file, category, start, rows, project_id
def publish(params):
	msg = json.dumps(params)
	msg_props = pika.BasicProperties()
	msg_props.content_type = "application/json"

	channel.basic_publish(body=msg, 
						  exchange="spark-exchange", 
						  properties=msg_props, 
						  routing_key="msg-filter")


if __name__ == '__main__':
	credentials = pika.PlainCredentials(settings.RABBITMQ_USERNAME, settings.RABBITMQ_PASSWORD)
	conn_params = pika.ConnectionParameters(settings.RABBITMQ_HOST, credentials=credentials)
	conn_broker = pika.BlockingConnection(conn_params)

	channel = conn_broker.channel()
	channel.exchange_declare(exchange="spark-exchange",
                         type="direct",
                         passive=False,
                         durable=True,
                         auto_delete=False)
	if len(sys.argv) == 2:
		invoice_file = sys.argv[1]
	else:
		invoice_file = "invoice.yaml"
		
	interpret(invoice_file)
