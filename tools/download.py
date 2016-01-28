# -*- coding: utf-8 -*-
import os
import sys
import urllib2


class Downloader(object):
	"""docstring for Downloader"""
	def __init__(self, arg):
		super(Downloader, self).__init__()
		self.arg = arg

#!/usr/bin/python
#coding=utf8

import urllib2
import log
from dpark import DparkContext
import os
import decrypt
from multiprocessing  import Queue
Com_queue = Queue()

class download(object):
	def __init__(self):
		self.log = log.my_log.instance()
		self.decrypter = decrypt.decrypt("key")

	def download(self, url, dest_file_path, time_out=60, try_cnt=3):
		'''
		@brief: 下载url中的文件，并保存到dest_file_path
		@param url: 需要下载的url
		@param dest_file_path: 保存文件的路径
		'''
		if try_cnt <= 0:
			return False
		try:
			req = urllib2.Request(url)
			print url
			req.add_header("User-agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36")
			response = urllib2.urlopen(req, timeout=time_out)
			res = response.read()
			print 'Response Successed'
			if len(res) == 0:
				self.log.set_error_log("download %d failed\t%s\t"%(try_cnt, url))		
				ret = self.download(url.strip(), dest_file_path, time_out, try_cnt-1)
				if not ret:
					return False
				else:
					return True
			with open(dest_file_path, "wb") as fp:
				fp.write(res)
			self.decrypter.decrypt(dest_file_path, dest_file_path[:-4])
			Com_queue.put('\\'.join(dest_file_path.split('\\')[:-1]))
			self.log.set_debug_log("download %d success\t%s"%(try_cnt, url))		
			return True
		except Exception as e:
			self.log.set_error_log("download %d failed\t%s\t%s"%(try_cnt, url, str(e)))		
			ret = self.download(url, dest_file_path, time_out, try_cnt-1)
			if not ret:
				return False
			else:
				return True

'''cut_path = "/home/hou/9000data"
def write_to_wav(line):
        file_name = line.split('\t')[0]
        if not os.path.exists(os.path.join(cut_path, file_name)):
                os.mkdir(os.path.join(cut_path, file_name))
                
        wav_name = line.split('\t')[1].split('/')[-1].split('_')[:-3]
        wav_name = '_'.join(wav_name)
        
        if not os.path.exists(os.path.join(cut_path, file_name, wav_name)):
                os.mkdir(os.path.join(cut_path, file_name, wav_name))
                
        dtemp = download().download(line.split('\t')[1].strip(), os.path.join(cut_path, file_name, wav_name, line.split('\t')[1].split('/')[-1].strip()))
'''
cut_path = r"D:\9000data\data".decode('utf8')
def write_to_wav(line):
    file_name = line.strip().split('/')[-1]
    if not os.path.exists(os.path.join(cut_path, file_name[:-8])):
        os.mkdir(os.path.join(cut_path, file_name[:-8]))
    
    dtemp = download().download(line.strip(), os.path.join(cut_path, file_name[:-8], file_name))

        
def DownLoad(file_path):
        dpark = DparkContext()
        file_block = dpark.textFile(file_path,splitSize=16<<20)
        file_block.foreach(write_to_wav)
        
if __name__ == "__main__":
        
	#dl = download()
	#print(dl.download("http://crowdfile.blob.core.chinacloudapi.cn/1548/1548_1980/918554_1548_1980_460467922.wav.enc", "C:\Users\size\Desktop\new_cut_wav\util", 20, 3))
        DownLoad(r'D:\9000data\wuyuanduan.txt'.decode('utf8'))
        
