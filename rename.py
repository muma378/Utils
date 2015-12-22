#!/usr/bin/python
# rename.py - usage: python rename.py script1.py script2.py ...
# To rename programes executed by python in the task manager
# author: xiao yang
# date: 2015.12.22

import sys 
import os
import subprocess

def get_exe_path():
	return sys.executable

def alter_exe_name(new_name):
	if new_name.endswith('.py'):
		new_name = new_name.replace('.py', '')
	if not new_name.endswith('exe'):
		new_name += '.exe'
	new_name = os.path.dirname(get_exe_path()) + '\\' + os.path.basename(new_name)
	cpy_command = 'COPY ' + get_exe_path() + ' ' + new_name
	subprocess.call(cpy_command, shell=True)	#generate a new python programe with a customized name
	return new_name 

def new_process(target_files):
	basename = os.path.basename(target_files) 
	new_programe = alter_exe_name(basename)
	exe_command = new_programe + ' ' + target_files
	subprocess.call(exe_command, shell=True)	#execute the duplicate python programe
	del_command = 'DEL ' + new_programe
	subprocess.call(del_command, shell=True)	#delete the duplicate programe
	return

def main():
	argc = len(sys.argv)
	if argc < 2 :
		print "no scripts is specified"
		exit()
	elif argc >= 2:
		file_counter = 1
		while file_counter < argc:
			new_process(sys.argv[file_counter])
			file_counter += 1

if __name__ == '__main__':
	main()