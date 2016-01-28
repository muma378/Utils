#!/usr/bin/python
#coding=utf8

from Crypto.Cipher import AES
import struct
import os

class decrypt(object):
	def __init__(self, key_path):
		self.key = open(key_path, "rb").read()
		self.decryptor = AES.new(self.key)

	def decrypt(self, src_path, dest_path):
		try:
			src_fp = open(src_path, "rb")
			dest_fp = open(dest_path, "wb")
			data = src_fp.read(4096)
			while data:
				data_len = len(data)
				if data_len != 4096:
					new_data_len = (data_len/16+1) * 16
					data = "".join([data, "0"*(new_data_len-data_len)])
					data = self.decryptor.decrypt(data)
				else:
					data = self.decryptor.decrypt(data)
				dest_fp.write(data)
				data = src_fp.read(4096)
		except Exception as e:
			print(e)
			return False
		return True
		#open(dest_path, "wb").write(self.decryptor.decrypt(open(src_path, "rb").read()))

	def split_wav_info(self, wav_file, wav_real_file, info_file):
		try:
			wav_fp = open(wav_file, "rb")
			real_wav_fp = open(wav_real_file, "wb")
			real_wav_fp.write(wav_fp.read(4))
			wav_len_str = wav_fp.read(4)
			real_wav_fp.write(wav_len_str)
			wav_len = struct.unpack("i", wav_len_str)[0]
			real_wav_fp.write(wav_fp.read(wav_len))
			open(info_file, "wb").write(wav_fp.read())
		except Exception as e:
			print(e)
			return False
		return True

	def wav_to_pm3(self, wav_file, mp3_file):
		try:
			os.popen("./driver %s %s"%(wav_file, mp3_file))	
		except:
			return False
			pass
		return True


if __name__ == "__main__":
	'''dc = decrypt("../processer/key")
	dc.decrypt("1.enc", "1.wav")
	#dc.split_wav_info("../data/2015-06-28wav/886524_1547_38_1435132474111.wav", "data.wav", "data.info")'''
        decrypt('../processer/key').wav_to_pm3('/home/hou/20150717_184716_2_5.04_8.595.wav','/home/hou/20150717_184716_2_5.04_8.595.mp3')
