#!/usr/bin/python
#coding=utf8

import log
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import configure

class send_email(object):
	def __init__(self, smtpserver, sender, username, password, receiver):
		'''
		@brief: 发送邮件模块的init，初始化发送者接受者等信息
		@param smtpserver: 发送者的邮箱服务器
		@param sender: 发送者的邮箱
		@param username: 发送者的邮箱名
		@param password: 发送者的邮箱密码
		@param receiver: 接受者的邮箱
		@param subject: 邮件标题
		@return: 失败False 成功True
		'''
		self.smtpserver = smtpserver
		self.sender = sender
		self.username = username
		self.password = password
		self.receiver = receiver
		self.log = log.my_log.instance()
	
	def send_one_email(self, subject, msg):
		'''
		@brief: 发送一个邮件
		@param subject: 邮件标题 utf8字符串
		@param msg: 邮件内容 utf8字符串
		@return: 失败False 成功True

		'''
		try:
			messgae = MIMEText(msg, "text", "utf-8")
			messgae["Subject"] = Header(subject, "utf-8")
			smtp = smtplib.SMTP()
			smtp.connect(self.smtpserver)
			smtp.login(self.username, self.password)
			smtp.sendmail(self.sender, self.receiver, messgae.as_string())
			smtp.quit()
			return True
		except Exception as e:
			self.log.set_error_log("send messgae error\t%s"%str(e))
			return False


if __name__ == "__main__":
	sde = send_email("smtp.163.com",
					"piaotiejun01@163.com",
					"piaotiejun01",
					"1990221",
					"piaotiejun@datatang.com")
	sde.send_one_email("aaaaa", "test subject")
