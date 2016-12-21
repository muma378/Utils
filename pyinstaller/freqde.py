# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import multiprocessing


# Module multiprocessing is organized differently in Python 3.4+
try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking

if sys.platform.startswith('win'):
    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen

def resource_path(relative_path):
	try:
		basepath = sys._MEIPASS
	except Exception, e:
		basepath = os.path.abspath('.')
	return os.path.join(basepath, relative_path)


# generator version of traversing
def traverser(src_dir, dst_dir, target='.wav', err=sys.stderr):
    for dirpath, dirnames, filenames in os.walk(src_dir):
        for filename in filenames:
            if filename.endswith(target):
                try:
                    src_file = os.path.join(dirpath, filename)
                    src_dir_len = len(src_dir) if src_dir.endswith(os.sep) else len(src_dir)+1
                    dst_file = os.path.join(dst_dir, src_file[src_dir_len:])    # should not use replace
                    yield src_file, dst_file
                except Exception as e:
                    err.write("unable to process {filename} for {reason}\n".format(filename=src_file, reason=e))

def evaluate(files_queue, result_queue):
	while True:
		src_file = files_queue.get()
		result = subprocess.check_output(
								[resource_path('freqde_win.exe'), src_file],
								stderr=subprocess.STDOUT,
								shell=True)
		result_queue.put(result.strip())
		files_queue.task_done()

def main(dirpath):
	files_queue = multiprocessing.JoinableQueue()
	result_queue = multiprocessing.Queue()
	for src_file, _ in traverser(dirpath, '', target='.wav'):
		files_queue.put(src_file)

	for i in range(multiprocessing.cpu_count()):
		p = multiprocessing.Process(target=evaluate, args=(files_queue, result_queue))
		p.daemon = True
		p.start()

	files_queue.join()

	with open(os.path.basename(dirpath)+'.log', 'w') as f:
		while not result_queue.empty():
			line = result_queue.get()
			f.write(line.decode('gbk').encode('utf-8'))
			f.write('\n')


if __name__ == '__main__':
	multiprocessing.freeze_support()
	if len(sys.argv) < 2:
		print("usage: freqde.py dirname [dirname]...")
		sys.exit(1)

	for path in sys.argv[1:]:
		if not os.path.isdir(path):
			print(u"指定的参数 {0} 不是文件夹或不存在".format(path.decode('gbk')).encode('gbk'))
			sys.exit(2)

	for path in sys.argv[1:]:
		main(path)