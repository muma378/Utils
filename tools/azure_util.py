#!/usr/bin/python
#coding=utf8

from azure.storage import *
import log
import configure

class azure_handler(object):
	def __init__(self):
		self.account = configure.azure_account #容器名
		self.account_key = configure.azure_account_key #容器对应的key值
		self.blob_host_base = configure.azure_blob_host_base #服务器
		self.queue_host_base = configure.azure_queue_host_base #服务器
		self.blob_service = BlobService(account_name=self.account, account_key=self.account_key, host_base=self.blob_host_base)
		self.queue_service = QueueService(account_name=self.account, account_key=self.account_key, host_base=self.queue_host_base)
		self.log = log.my_log.instance()

	def create_queue(self, queue_name):
		'''
		@brief: 创建队列
		@param queue_name: 队列名字 str
		@return: 失败False 成功True
		'''
		try:
			ret = self.queue_service.create_queue(queue_name)
		except Exception as e:
			print(e)
			return False
		return ret

	def set_queue_message(self, queue_name, message):
		'''
		@brief: 插入一条消息到队列中
		@param queue_name: 队列名字 str
		@param message: 消息 str
		@return: 失败False 成功True
		'''
		try:
			self.queue_service.put_message(queue_name, message)
		except Exception as e:
			print(e)
			return False
		return True

	def get_message(self, queue_name):
		'''
		@brief: 消费一条消息,即取出一条消息并从队列中删除该消息
		@param queue_name: 队列名字 str
		@return: 失败False 成功返回消息字符串
		'''
		try:
			message = self.queue_service.get_messages(queue_name)[0]
			self.queue_service.delete_message(queue_name, message.message_id, message.pop_receipt)
		except Exception as e:
			return False
		return message.message_text

	def delete_queue(self, queue_name):
		'''
		@brief: 删除队列
		@param queue_name: 队列名字 str
		@return: 失败False 成功True
		'''
		try:
			self.queue_service.delete_queue(queue_name)
		except Exception as e:
			print(e)
			return False
		return True

	def create_blob(self, blob_name):
		try:
			ret = self.blob_service.create_container(blob_name)
			return ret
		except Exception as e:
			print(e)
			return False

	def upload(self, blob_name, azure_file_name, file_path):
		'''
		@brief: 上传一个文件到云端,云端的文件名与本地文件名相同
		@param file_path: 上传的文件路径
		@return: 失败False 成功True
		'''
		try:
			self.log.set_debug_log("upload begin")
			
			self.blob_service.put_block_blob_from_path(blob_name, azure_file_name, file_path) #容器，云端文件名，本地文件名
			self.log.set_debug_log("upload end with success")
			return True
		except Exception as e:
			self.log.set_error_log("upload end with error\t%s\t%s"%(file_path, str(e)))
			return False

	def list_blob(self, container):
		'''
		@brief: list container 
		@param container: container名字
		'''
		blobs = self.blob_service.list_blobs(container)
		for blob in blobs:
			print(blob.name)
			print(blob.url)

	def delete_blob(self, container, file_name):
		'''
		@brief: 删除container下的file_name
		@param container: 
		@pram file_name:
		@return: 成功True 失败False
		'''
		try:
			self.blob_service.delete_blob(container, file_name)
			return True
		except Exception as e:
			self.log.set_error_log("delete_blob error\t%s\t%s"%(file_name, str(e)))
			return False

if __name__ == "__main__":
	ah = azure_handler()
#	ah.delete_queue("autocut")
#	ah.create_queue("autocut")
#	for i in xrange(10):
#		ah.set_queue_message("autocut", "hello world\t"+str(i))
#	for data in xrange(5):
#		print(ah.get_message("autocut"))

#	ah.upload("")
#	ah.delete_blob("1124", "cut_audio")
	ah.list_blob("1547")


