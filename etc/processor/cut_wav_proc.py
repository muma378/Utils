#!/usr/bin/python
#coding=utf8

from multiprocessing import Process, Queue, Lock
import time
import os
import sys
import json
import random
import base64
if "../util/" not in sys.path:
	sys.path.append("../util/")
import log
import db_handler
import set_demon
import decrypt
import download
import cut_audio
import azure_util
import configure
import BloomFilter


class cut_wav_handler(object):
	def __init__(self):
		self.sqlserver = db_handler.sqlserver_handler()
		self.log = log.my_log.instance()
		self.cut_audio = cut_audio.audio_cut()
		self.azure = azure_util.azure_handler()
		self.decrypter = decrypt.decrypt("key")
		self.BloomFilter = BloomFilter.BloomFilter(0.001,3000000) 
		self.azure.create_queue(configure.cutted_queue)
		self.azure.create_blob(configure.cutted_blob)
		self.tag_task_list = configure.tag_task_list
		self.data_cnt = 0

	def set_random_json(self, url, time_len):
		task_id = ""
		rand = random.randint(1, 100)		
		for data in self.tag_task_list:
			if rand > data[1]:
				task_id = data[0]
		task_dic = {}
		task_dic["url"] = url
		task_dic["task_id"] = task_id
		task_dic["time_len"] = time_len
		return json.dumps(task_dic)

	def get_abs_file_list(self, file_path):
		if not os.path.exists(file_path):
			print("file path error\t%s"%file_path)
			return []
		file_list_all = []
		result_list = []
		file_list_all.append(file_path)
		while len(file_list_all) != 0:
			work_file = file_list_all.pop(0)
			if not os.path.isdir(work_file):
				if work_file.find("wav") >= 0:
				   result_list.append(work_file)
			else:
				file_list_all.extend([os.path.join(work_file, fi) for fi in os.listdir(work_file)])
		return result_list

	def cut_wav_per_1_day(self, file_home, cutted_path,cutted_log,up_mp3_log,up_wav_log):
			cut_data = self.log.get_cur_day()
			need_cutted_list = self.get_abs_file_list(file_home)
			cutted_home = "".join([cutted_path,"cutted"])
			#cut wav and upload
			bfp = open(cutted_log,'r')
			for line in bfp.readlines():
				self.BloomFilter.insert_element(line.strip())
			fp = open(cutted_log, "a+")
			up_wav_error = open(up_wav_log,"a+")
			up_mp3_error = open(up_mp3_log,"a+")	  
			for wav_real_file in need_cutted_list:
				if self.BloomFilter.is_element_exist(wav_real_file.strip().split('/')[-1]) == False:
					fp.write(wav_real_file.strip().split('/')[-1]+"\n")
					fp.flush()
					if not os.path.exists(cutted_home):
						os.makedirs(cutted_home)
					ret = self.cut_audio.cut_one_audio(wav_real_file, cutted_home)
					if not ret:
						print("cut failed")
						continue
					else:
						for data in ret:
							cutted_file = data[0]
							time_len = data[1]	
							url = "".join(["http://crowdfile.blob.core.chinacloudapi.cn/", \
							configure.cutted_blob, "/", cutted_file.split("/")[-1]])									 
							mp3_file = cutted_file[:-4]+".mp3"
							if os.path.getsize(cutted_file)/1024.0 >= 13:
								self.data_cnt += 1
							if not self.decrypter.wav_to_pm3(cutted_file, mp3_file):
								print("wav to mp3 error")
								continue
							else:
								print("wav to mp3 success")

							if not self.azure.upload(configure.cutted_blob, cutted_file.split("/")[-1], cutted_file):
								print("upload wav error")
								up_wav_error.write(wav_real_file.split('/')[-1]+"\n")
								continue
							else:
								print("upload wav success")

							if not self.azure.upload(configure.cutted_blob, mp3_file.split("/")[-1], mp3_file):
								print("upload mp3 error")
								up_mp3_error.write(wav_real_file.split('/')[-1]+"\n")
								continue
							else:
								print("upload mp3 success")

							json_str = self.set_random_json(url, time_len)
							if self.azure.set_queue_message(configure.cutted_queue, \
								base64.encodestring(json_str)):
								print("set message success")
							else:
								print("set message error")
			fp.close()
			#time.sleep(60*60)

wav_path = r"/media/hou/Elements/9000小时项目切割数据/4第四次切割501-0818/合格数据"
cut_path = "/media/hou/cut-wav-1"
if __name__ == "__main__":
	#processHandler()
		#sql = "SELECT B.FileName FROM [CrowdDB].[dbo].[QualityData] as A left join CrowdDB.dbo.DataAcquisition as B on A.DataGuid = B.DataGuid where A.ProjectId=%s and A.Status=1547"
		#cut_wav_handler().cut_wav_per_1_day(sql, "", "../data_%s/"%1547, "../log/wav_cutted_list_%s"%15)
				cut_wav =  cut_wav_handler()
				for line in os.listdir(wav_path):
					cut_wav.cut_wav_per_1_day(os.path.join(wav_path,line),os.path.join(cut_path,line),'/media/hou/audio-cut/log/wav_cutted','/media/hou/audio-cut/log/up_mp3_error','/media/hou/audio-cut/log/up_wav_error')
