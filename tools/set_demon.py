#!/usr/bin/python
#coding=utf-8
#设置为守护进程

import os,sys,commands,time

def daemonize(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
	"""
	@brief: set daemonize
	@param stdin: 重定向标准输入的文件
	@param stdout: 重定向标准输出的文件
	@param stderr: 重定向标准错误的文件
	"""
	try: #使当前进程不再是进程组组长
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except Exception as e:
		print("fork failed\t%s"%str(e))
		sys.exit(0)
	
	os.setsid() #使当前进程成为会话首进程、进程组首进程
	os.chdir('.') #设置工作目录
	os.umask(0) #修改权限
	
	#将标注IO重定向，使该进程脱离终端,不接受终端的信号
	si = open(stdin, "r")
	so = open(stdout, "a+")
	se = open(stderr, "a+")
	pid = str(os.getpid())
	print("start with pid :[%s]"%pid)
	with open("pid", "w") as fp:
		fp.write(pid)
	sys.stderr.flush()
	sys.stdout.flush()
	sys.stderr.flush()
	os.dup2(si.fileno(), sys.stdin.fileno()) #重定向
	os.dup2(so.fileno(), sys.stdout.fileno())
	os.dup2(se.fileno(), sys.stderr.fileno())

def main():
	daemonize()
	cmd = "ls" 
	while 1:
		status, ret = commands.getstatusoutput(cmd)
		print status
		print ret      
		time.sleep(10)

if __name__ == "__main__":
	main()
