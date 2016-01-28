#!/usr/bin/python
#coding=utf8

import struct
import os
import handle_file
class wav_data(object):
	def __init__(self):
		pass

	def write_wav(self, wav_file_path, wav_len, wav_fmt_len, wav_pcm_code, wav_channels, wav_sample_rate, wav_byte_rate, \
		wav_block, sample_byte_len, pcm_len, pcm_data):
		'''
		@brief: 写wav文件
		@param ***: wav的各种参数
		@return: 成功True 失败False
		'''
		try:
			fp = open(wav_file_path, "wb")
		except Exception as e:
			print(e)
			return False
		try:
			fp.write("RIFF")
			fp.write(struct.pack("i", wav_len))
			fp.write("WAVE")
			fp.write("fmt ")
			fp.write(struct.pack("i", wav_fmt_len))
			fp.write(struct.pack("h", wav_pcm_code))
			fp.write(struct.pack("h", wav_channels))
			fp.write(struct.pack("i", wav_sample_rate))
			fp.write(struct.pack("i", wav_byte_rate))
			fp.write(struct.pack("h", wav_block))
			fp.write(struct.pack("h", sample_byte_len))
			fp.write("data")
			fp.write(struct.pack("i", pcm_len))
			for data in pcm_data:
				fp.write(struct.pack("h", data))
			return True
		except Exception as e:
			print(e)
			return False

	def read_wav(self, wav_file_path):
		'''
		@brief: 读取wav文件
		@param wav_file_path: wav文件路径
		@return: 失败False 成功True
		'''
		self.wav_file_path = wav_file_path
		try:
			wav_fp = open(wav_file_path, "rb")
			self.wav_riff = wav_fp.read(4)
			self.wav_len = struct.unpack("i", wav_fp.read(4))[0]
			self.wav_flag = wav_fp.read(4)
			self.wav_fmt_flag = wav_fp.read(4)
			self.wav_fmt_len = struct.unpack("i", wav_fp.read(4))[0]
			self.wav_pcm_code = struct.unpack("h", wav_fp.read(2))[0]
			self.wav_channels = struct.unpack("h", wav_fp.read(2))[0]
			self.wav_sample_rate = struct.unpack("i", wav_fp.read(4))[0]
			self.wav_byte_rate = struct.unpack("i", wav_fp.read(4))[0]
			self.wav_block = struct.unpack("h", wav_fp.read(2))[0]
			self.sample_byte_len = struct.unpack("h", wav_fp.read(2))[0]
			self.wav_data_flag = wav_fp.read(4)
			if self.wav_data_flag != "data":
				print("44 is not data")
				return False
			self.pcm_len = struct.unpack("i", wav_fp.read(4))[0]
			self.wav_one_sample_time = 1.0 / self.wav_sample_rate
			self.pcm_data = []
			sample = wav_fp.read(2)
			while sample:
				self.pcm_data.append(struct.unpack("h", sample)[0])
				sample = wav_fp.read(2)
			self.wav_time_len = len(self.pcm_data) * self.wav_one_sample_time
		except Exception as e:
			print(e)
			return False
		return True


class wav_cut(object):
	def __init__(self):
		pass

	def cut_wav(self, wav_file_path, wav_cutted_dest_path, timelist, time_span, energy_thrd, zero_thrd):
		'''
		@brief: 切割wav文件
		@param wav_file_path: 需要被切割的wav文件路径
		@param wav_cutted_dest_path: 保存wav文件的路径
		@param time_span: 一个窗函数的长度 单位s
		@param energy_thrd: 能量阀值 平均能量的比例
		@param zero_thrd: 短时过零率阀值
		@return: 失败False 成功True
		'''
		one_wav = wav_data()
		if not one_wav.read_wav(wav_file_path):
			print("open wav failed")
			return False
		pcm_data = one_wav.pcm_data
		one_sample_rate = 1.0 / one_wav.wav_sample_rate
		res_file_list = []
		counter = 0
		for wavtime in timelist:
                        start = float(wavtime[0]) / one_sample_rate
                        end = float(wavtime[1]) / one_sample_rate
			
                        cutted_wav_file_name = os.path.join(wav_cutted_dest_path, wav_file_path.split("\\")[-1][:-4]+ "_" + \
				str(start*one_wav.wav_one_sample_time) + "_" + str(end*one_wav.wav_one_sample_time) + ".wav")
			
			cutted_wav = wav_data()
			print 'start: ', start*one_sample_rate, 'end: ', end*one_sample_rate
			if not cutted_wav.write_wav(cutted_wav_file_name, (end-start)*2+36, one_wav.wav_fmt_len, one_wav.wav_pcm_code, \
						    one_wav.wav_channels, one_wav.wav_sample_rate, one_wav.wav_byte_rate, one_wav.wav_block, \
						    one_wav.sample_byte_len, (end-start)*2, pcm_data[int(start):int(end)]):
				print("write wav failed")
				return False
			res_file_list.append((cutted_wav_file_name, (end-start)*one_wav.wav_one_sample_time))
			counter += 1
		return res_file_list


if __name__ == "__main__":
	wav_c = wav_cut()
	'''for fi in [os.path.join("/media/piaotiejun-usr/Elements/C_T/", f) for f in os.listdir("/media/piaotiejun-usr/Elements/C_T/")]:
		if not wav_c.cut_wav(fi, "/media/piaotiejun-usr/Elements/piaotiejun_cutted/", 0.01, 0.6, 80):
			print("\n\nerror\n\n")
		else:
			print("success")'''
	timelist = handle_file.handle_file().groupbyname(r'C:\Users\size\Desktop\new_cut\WavCutTool\seg_utf8.list.out')
	wavname = r'20150724_214713.wav'
	wav_c.cut_wav(r'C:\Users\size\Desktop\new_cut\0\20150724_214713.wav', r'C:\Users\size\Desktop\new_cut\0\fa', timelist[wavname], 0.01, 0.6, 80)
	print 'successed'

