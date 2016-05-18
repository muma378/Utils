#!/usr/bin/python
#coding=utf8

from Crypto.Cipher import AES
import os
import sys
if "../util/" not in sys.path:
	sys.path.append("../util/")
import decrypt
import azure_util
import configure
from wav_cut import wav_data



temp_path = "./temp"
azure = azure_util.azure_handler()

def encrypt(src_path, dest_path):
	"""
	@brief: 加密
	"""
	key = open("key", "rb").read()
	decryptor = AES.new(key)
	try:
		src_fp = open(src_path, "rb")
		dest_fp = open(dest_path, "wb")
		data = src_fp.read(4096)
		while data:
			data_len = len(data)
			if data_len != 4096:
				new_data_len = (data_len/16+1) * 16
				data = "".join([data, "0"*(new_data_len-data_len)])
				data = decryptor.encrypt(data)
			else:
				data = decryptor.encrypt(data)
			dest_fp.write(data)
			data = src_fp.read(4096)
	except Exception as e:
		print(e)
		return False
	return True


def handler_one_wav(file_path):
	is_decryptted = True
	one_wav = wav_data()
	dest_path = os.path.join(temp_path, file_path.split("/")[-1]) + ".enc"
	if one_wav.read_wav(file_path): #un-decryptted
		encrypt(file_path, dest_path)
		is_decryptted = False 
		pass
	else: #decryptted
		wav_file = os.path.join(temp_path, file_path.split("/")[-1][:-4])
		decrypter = decrypt.decrypt("key")
		decrypter.decrypt(file_path, wav_file)
		one_wav = wav_data()
		one_wav.read_wav(wav_file)
	if one_wav.wav_channels != 1:
		return
	if one_wav.wav_sample_rate != 16000:
		return

	tmp_list = dest_path.split("/")[-1].split("_")
	task_id = tmp_list[1]
	azure_file_name = "_".join([tmp_list[1], tmp_list[2]]) + "/" + dest_path.split("/")[-1]
	print(azure_file_name)
	if is_decryptted:
		#upload file_path
		print("decryptted")
		azure.upload(task_id, azure_file_name, file_path)
	else:
		#upload dest_path
		print("un-decryptted")
		azure.upload(task_id, azure_file_name, dest_path)

if __name__ == "__main__":
	handler_one_wav("999991136_20000_49_1435977547019.wav.enc")

