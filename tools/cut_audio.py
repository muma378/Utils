#!/usr/bin/python
#coding=utf8

import os
import log
import wav_cut

class audio_cut(object):
	def __init__(self):
		self.log = log.my_log.instance()
		self.wav_cut = wav_cut.wav_cut()
	
	def cut_one_audio(self, file_path, dest_path, timelist):
		'''
		@brief: 切割一个音频文件
		@param file_path: 需要被切割文件路径
		@param dest_path: 保存切割后的小文件的文件夹路径
		@return: 失败False 成功True
		'''
		ret = []
		self.log.set_debug_log("begin cut audio\t%s"%file_path)
		try:
			ret = self.wav_cut.cut_wav(file_path, dest_path, timelist, 0.01, 0.6, 80)
			if not ret:
				print("cut audio failed")
				return False
		except Exception as e:
			self.log.set_error_log("cut audio error\t%s\t%s"%(file_path, str(e)))
			return False
		self.log.set_debug_log("cut audio success\t%s"%file_path)
		return ret

if __name__ == "__main__":
	ac = audio_cut()
	top_dir = "/media/piaotiejun-usr/Elements/9000h/piaotiejun_out/1/"
	dest_dir = "/media/piaotiejun-usr/Elements/cutted_test/"
	cnt = 0
	for wav in [os.path.join(top_dir, fi) for fi in os.listdir(top_dir)]:
		print(cnt)
		cnt += 1
		ac.cut_one_audio(wav, dest_dir)
	print("end")

