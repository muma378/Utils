#!/usr/bin/python
#coding=utf8

from multiprocessing import Process, Queue, Lock
import threading
import time
import os
import sys
if "../util/" not in sys.path:
	sys.path.append("../util/")
import log
import db_handler
import cut_audio
import set_demon
import decrypt
import download
import azure_util
import configure


class decrypt_handler(object):
	def __init__(self):
		self.sqlserver = db_handler.sqlserver_handler()
		self.log = log.my_log.instance()
		self.downloader = download.download()
		self.decrypter = decrypt.decrypt("key")
		self.azure = azure_util.azure_handler()
		for queue in configure.queue_list:
			self.azure.create_queue(queue)

	def get_unhandled_file_list(self, sql, enc_url_log_path, queue_name):
		'''
		@brief: 时时获取enc file list,并写入队列,将写入对列的enc url写入文件
		@param enc_url_log_path: 保存enc file list的文件路径
		@return: 线程函数无返回值
		'''
		while True:
			enc_url_list = self.sqlserver.exec_query(sql)
			print("sqlserver url %s len is:\t"%queue_name+str(len(enc_url_list)))
			enc_url_dic = {}
			if os.path.exists(enc_url_log_path):
				fp = open(enc_url_log_path, "r")
				for line in fp:
					enc_url_dic[line.strip()] = 1
				fp.close()
			print("my dic url %s len is:\t"%queue_name+str(len(enc_url_dic)))
			for enc_url in enc_url_list:
				enc_url = enc_url[0].encode("utf8")
				if enc_url not in enc_url_dic:
					self.azure.set_queue_message(queue_name, enc_url)
			time.sleep(10*60)

	def decrypt_enc_file(self, file_home, enc_url_log_path, queue_name):
		'''
		@brief: 解密数据
		@param enc_home: 保存enc文件的文件夹
		@param wav_home: 保存解密出的文件的文件夹
		@param wav_real_home: 保存wav与info的文件夹
		@param cutted_home: 保存切割后的wav文件的文件夹
		@return: 失败False 成功True
		'''
		enc_url_dic = {}
		if os.path.exists(enc_url_log_path):
			fp = open(enc_url_log_path, "r")
			for line in fp:
				enc_url_dic[line.strip()] = 1
			fp.close()
		fp = open(enc_url_log_path, "a+")
		while True:
			if not os.path.exists(file_home):
				os.makedirs(file_home)
			cur_day = self.log.get_cur_day()
			enc_home = "".join([file_home, cur_day, "enc"])
			wav_home = "".join([file_home, cur_day, "wav"])
			wav_real_home = "".join([file_home, cur_day, "wav_real"])
			cutted_home = "".join([file_home, cur_day, "cutted"])
			mp3_home = "".join([file_home, cur_day, "mp3"])
			if not os.path.exists(enc_home):
				os.makedirs(enc_home)
			if not os.path.exists(wav_home):
				os.makedirs(wav_home)
			if not os.path.exists(wav_real_home):
				os.makedirs(wav_real_home)
			if not os.path.exists(cutted_home):
				os.makedirs(cutted_home)
			if not os.path.exists(mp3_home):
				os.makedirs(mp3_home)
			message = self.azure.get_message(queue_name)
			if message:
				if message in enc_url_dic:
					print("\nalready exist\n")
					continue
				enc_url_dic[message] = 1
				fp.write(message+"\n")
				fp.flush()
				file_name = message.split("/")[-1]
				enc_file = os.path.join(enc_home, file_name)
				wav_file = os.path.join(wav_home, file_name)[:-4]
				wav_real_file = os.path.join(wav_real_home, file_name)[:-4]
				mp3_file = os.path.join(mp3_home, file_name)[:-8] + ".mp3"
				info_file = os.path.join(wav_real_home, file_name)[:-4] + ".info"
				if not self.downloader.download(message, enc_file, 20, 3):
					continue
				else:
					print("download success %s"%queue_name)
				if not self.decrypter.decrypt(enc_file, wav_file):
					continue
				else:
					print("decrypt success %s"%queue_name)
				if not self.decrypter.split_wav_info(wav_file, wav_real_file, info_file):
					continue
				else:
					print("split info success %s"%queue_name)
				if not self.decrypter.wav_to_pm3(wav_real_file, mp3_file):
					continue
				else:
					print("wav to mp3 success %s"%queue_name)
				task_id = queue_name.split("-")[-1]
				azure_file_name = message.split("chinacloudapi.cn/%s/"%task_id)[-1][:-4]
				azure_mp3_name = message.split("chinacloudapi.cn/%s/"%task_id)[-1][:-8] + ".mp3"
				if not self.azure.upload(task_id, azure_file_name, wav_real_file):
					continue
				else:
					print("upload wav success %s"%queue_name)
				if not self.azure.upload(task_id, azure_mp3_name, mp3_file):
					continue
				else:
					print("upload mp3 success %s"%queue_name)
			else:
				time.sleep(60)


def processHandler():
	sql_proc_pool = []
	task_list = configure.task_list
	decrypter = decrypt_handler()
	for i in xrange(len(task_list)):
		sql = "select FileName from CrowdDB.dbo.DataAcquisition where ProjectId=%s"%task_list[i]
		enc_list_process = Process(target=decrypter.get_unhandled_file_list, args=(sql, "../log/enc_file_list_%s"%task_list[i], configure.azure_queue_name%task_list[i]))
		sql_proc_pool.append(enc_list_process)
		enc_list_process.start()

	process_pool = []
	for i in xrange(len(task_list)):
		decrypter = decrypt_handler()
		process = Process(target=decrypter.decrypt_enc_file, args=("../data_%s/"%task_list[i], "../log/enc_file_list_%s"%task_list[i], configure.azure_queue_name%task_list[i]))
		process_pool.append(process)
		process.start()

	for process in process_pool:
		process.join()
	for process in sql_proc_pool:
		process.join()
	print("end with success")


if __name__ == "__main__":
	processHandler()



