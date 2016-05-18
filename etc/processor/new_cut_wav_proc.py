#!/usr/bin/python
#coding=utf8

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
import filter_audio
import handle_file

from multiprocessing import Process
from multiprocessing import Pool
from multiprocessing import Manager

cut_path = r"C:\Users\size\Desktop\new_cut\cutted"
class cut_wav_handler(object):

    def __init__(self):
        self.sqlserver = db_handler.sqlserver_handler()
        self.log = log.my_log.instance()
        self.cut_audio = cut_audio.audio_cut()
        self.azure = azure_util.azure_handler()
        self.BloomFilter = BloomFilter.BloomFilter(0.001,30000000)
        self.azure.create_queue(configure.cutted_queue)
        self.azure.create_blob(configure.cutted_blob)
        self.decrypter = decrypt.decrypt("key")
        self.tag_task_list = configure.tag_task_list
        self.decrypter_flag = False
        self.all_time = 0.0
        self.Time_Unqualified = 0.0

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

    def set_decrypter(self, decrypter):
        self.decrypter_flag = True
        self.decrypter_func = decrypter

    def set_filter_audio(self, filter_audio):
        self.filter_audio = filter_audio

    def set_other_log(self, cutted_log,
                      up_wav_log,
                      up_mp3_log,
                      cut_file_log,
                      open_wav_faile_log,
                      wav_to_mp3_log,
                      long_time_file_log):
        self.cutted_log = cutted_log 
        self.up_wav_log = up_wav_log
        self.up_mp3_log = up_mp3_log
        self.cut_file_log = cut_file_log
        self.wav_to_mp3_log = wav_to_mp3_log
        self.open_wav_faile_log = open_wav_faile_log
        self.long_time_file_log = long_time_file_log
        
    
    def updata(self, wavData, up_wav_error, up_mp3_error, cut_wav_error, wav_to_mp3, open_wav_file, long_time_waring):
        for data in wavData:
            cutted_file = data[0]
            ime_len = data[1]
            url = "".join(["http://crowdfile.blob.core.chinacloudapi.cn/", \
            configure.cutted_blob, "/", cutted_file.split("/")[-1]])
            mp3_file = cutted_file[:-4]+'.mp3'
            if self.filter_audio(cutted_file,time_len):
                self.all_time += float(time_len)
                            
                if float(time_len) >= 1.0:
                    if not self.decrypter.wav_to_pm3(cutted_file,mp3_file):
                        print "wav to mp3 error"
                        wav_to_mp3_error.write(cutted_file.strip()+'\n')
                        continue
                    else:
                        print "wav to mp3 success"

                    if not self.azure.upload(configure.cutted_blob,cutted_file.split('\\')[-1],cutted_file):
                        print "upload wav error"
                        up_wav_error.write(cutted_file.strip()+'\n')
                        continue
                    else:
                        print "upload success"

                    if not self.azure.upload(configure.cutted_blob,mp3_file.split('\\')[-1],mp3_file):
                        print "upload mp3 error"
                        up_mp3_error.write(cutted_file.strip()+'\n')
                        continue
                    else:
                        print "upload mp3 success"

                    json_str = self.set_random_json(url,time_len)
                    if self.azure.set_queue_message(configure.cutted_queue,\
                                                            base64.encodestring(json_str)):
                        print "set message success"
                    else:
                        print "set message error"
                                    
            else:
                self.Time_Unqualified += float(time_len)
                if float(time_len) > 20:
                    long_time_waring.write(cutted_file.strip()+'\n')
    
    def cut_wav_per_1_day(self, file_home, cutted_path):
        cut_data = self.log.get_cur_day()
        cutted_home = "".join([cutted_path,"cutted"])

        #perl脚本
        perl_strip = 'C:\\Users\\size\\Desktop\\new_cut\\WavCutTool\\run_bat.pl'

        fp = open(self.cutted_log, 'a+')
        up_wav_error = open(self.up_wav_log, "a+")
        up_mp3_error = open(self.up_mp3_log, "a+")
        cut_wav_error = open(self.cut_file_log, "a+")
        wav_to_mp3_error = open(self.wav_to_mp3_log, "a+")
        open_wav_file = open(self.open_wav_faile_log, "a+")
        long_time_waring = open(self.long_time_file_log,"a+")

        print file_home,cutted_path
        Fild = handle_file.handle_file() 
        if not os.path.exists(cutted_home):
            os.makedirs(cutted_home)
        print 'perl %s %s' % (perl_strip, file_home)
        
        os.system('perl C:\\Users\\size\\Desktop\\new_cut\\WavCutTool\\run_bat.pl C:\\Users\\size\\Desktop\\new_cut\\0\\20150724_214713')

        raw_input()
        FileDict = Fild.groupbyname(os.path.join(file_home, 'seg_utf8.list.out'))
        wavFile = self.get_abs_file_list(file_home)

        for line in wavFile:
            if not self.BloomFilter.is_element_exist('\\'.join(line.split('\\')[-2:])):
                self.BloomFilter.insert_element('\\'.join(line.split('\\')[-2:]))
                fp.write('\\'.join(line.split('\\')[-2:])+'\n')
                fp.flush()
                if self.decrypter_flag:
                    '''解密 修改切割路径'''
                    if wav_real_file.find('enc'):
                        self.decrypter_func(wav_real_file,wav_real_file[:-4])
                        wav_real_file = wav_real_file[:-4]		    

                wavName = line.split('\\')[-1]
                ret = self.cut_audio.cut_one_audio(line, cutted_home, FileDict[wavName])
                if not ret:
                    print "cut failed"
                    cut_wav_error.write(wav_real_file.strip()+'\n')
                    continue
                else:
                    self.updata(ret, up_wav_error, up_mp3_error, cut_wav_error, wav_to_mp3, open_wav_file, long_time_waring)
                    
        fp.close()
        up_wav_error.close()
        up_mp3_error.close()
        cut_wav_error.close()
        wav_to_mp3_error.close()
        open_wav_file.close()
        long_time_waring.close()

    def cut_audio_main(self, cut_audio_path, cutted_log, MultNum):
        self.set_filter_audio(filter_audio.filter_audio().filter_by_time)
        time_result_log = open(r'C:\Users\size\Desktop\new_cut\audio_cut\log\time_result_log',"a+")   
        self.set_other_log(r'C:\Users\size\Desktop\new_cut\audio_cut\log\wav_cutted',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\up_wav_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\up_mp3_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\cut_wav_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\wav_to_mp3_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\open_wav_file_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\long_time_file_error'
                          )
    
        bfp = open(cutted_log, 'r')
        for line in bfp.readlines():
            self.BloomFilter.insert_element(line.strip())
    
        pool = Pool(processes = MultNum)
    
        for line in os.listdir(cut_audio_path):
            pool.map(self.cut_wav_per_1_day, (os.path.join(cut_audio_path,line), os.path.join(cut_path,line)))
        pool.close()
        pool.join()

	
        time_result_log.write('All Cut Time:'+str(cut_wav.all_time)+'\n')
        time_result_log.write('Time Unqualified:'+str(cut_wav.Time_Unqualified)+'\n')
    
#wav_path = "/home/hou/9000cutted_wuyuanduan"
def cut_audio_main(cut_audio_path,cutted_log, MultNum):
    cut_wav = cut_wav_handler()
    cut_wav.set_filter_audio(filter_audio.filter_audio().filter_by_time)
    #cut_wav.set_decrypter()
    time_result_log = open(r'C:\Users\size\Desktop\new_cut\audio_cut\log\time_result_log',"a+")   
    cut_wav.set_other_log(r'C:\Users\size\Desktop\new_cut\audio_cut\log\wav_cutted',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\up_wav_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\up_mp3_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\cut_wav_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\wav_to_mp3_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\open_wav_file_error',
                          r'C:\Users\size\Desktop\new_cut\audio_cut\log\long_time_file_error'
                          )
    
    bfp = open(cutted_log, 'r')
    for line in bfp.readlines():
        cut_wav.BloomFilter.insert_element(line.strip())
    
    pool = Pool(processes = MultNum)
    
    for line in os.listdir(cut_audio_path):
        cut_wav.cut_wav_per_1_day(os.path.join(cut_audio_path,line), os.path.join(cut_path,line))

	
    time_result_log.write('All Cut Time:'+str(cut_wav.all_time)+'\n')
    time_result_log.write('Time Unqualified:'+str(cut_wav.Time_Unqualified)+'\n')

if __name__ == "__main__":
    cut_audio_main(r'C:\Users\size\Desktop\new_cut\0', r'C:\Users\size\Desktop\new_cut\audio_cut\log\LOG', 3)
    print 'successed'
