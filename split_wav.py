# -*- coding: utf-8 -*-
import os
import sys
import re
import subprocess
from datetime import datetime
from traverse import traverse

TIME_FORMAT = '%M:%S.%f'
MILLION = 1000000.0
CMD_TEMPLATE = ('' if sys.platform=='win32' else './') + 'cut.exe "{src_file}" "{dst_file}" {start} {end}'
FRAGMENT_NAME_TEMPLATE = '_{marker}{index}.'
AUDIO_SUFFIX = '.wav'
IDENTIFIER_PATTERN = 'Task\d(?P<identifier>[a-zA-Z]+)\W.*'
DEFAULT_INDEX = 0

def time_convert(time_str):
	t = datetime.strptime(time_str.strip(), TIME_FORMAT)
	return str(t.hour*3600.0+t.minute*60+t.second+t.microsecond/MILLION)

def confirm(candidate, src):
	if candidate:
		print('The name matched for %s is %s' % (src, candidate))
		confirm = raw_input('Confirm?(press enter to use the default name)')
		if confirm:
			sys.exit(0)
	else:
		print('Unable to match any candidate for %s' % src)
		candidate = raw_input('Please specify the name manually:')
	return candidate


def find_similar(filename, target='.txt'):
	dirname = os.path.dirname(filename)
	basename = os.path.basename(filename)
	filenames = filter(lambda x: x.endswith(target), os.listdir(dirname))
	
	for i in range(len(basename)):
		pattern = basename[:-i] if i>0 else basename
		for target_file in filenames:
			if target_file.find(pattern) != -1:
				target_file = confirm(target_file, filename)

				return os.path.join(dirname, target_file)

def remove_suffix(filename):
	suffix = '.' + filename.split('.')[-1]
	return filename[:-len(suffix)]

def parse(filename, target='.txt', use_similar=False):
	fragments = []
	if use_similar:
		reference = find_similar(remove_suffix(filename), target)
	else:
		reference = remove_suffix(filename) + target

	with open(reference) as f:
		lineno = 0
		for line in f:
			lineno += 1
			if line.strip() == '':
				continue
			# clean before loading
			begining, ending, text = filter(lambda x: len(x.strip())!=0, line.split('\t'))
			try:
				fragments.append((time_convert(begining), time_convert(ending), text.strip()))
			except ValueError, e:
				print('line %d, unable to parse line %s' % (lineno, line))
				fragments.append(())	# an empty tuple as a place holder

	return fragments

def get_last_index(dst_dir, target='.txt', default=DEFAULT_INDEX):
	# import pdb;pdb.set_trace()
	filenames = filter(lambda x: x.endswith(target), os.listdir(dst_dir))
	last_index = default
	parser = re.compile('.*_(?P<index>\d+)'+target)
	for name in filenames:
		try:
			index = int(parser.match(name).group('index'))
			last_index = index if last_index < index else last_index
		except AttributeError, e:
			pass
	return last_index


def generate(src_file, dst_dir, fragments, fragment_name, identifier):
	mark = identifier[0]

	if not os.path.exists(dst_dir):
		os.makedirs(dst_dir)
		starter = 1
	else:
		starter = get_last_index(dst_dir) + 1

	for index, fragment in enumerate(fragments, start=starter):
		if len(fragment) == 0:
			continue

		text = fragment[-1]
		marker = mark+'_' if text.find('<'+mark+'>')!=-1 else ''

		# Avia_A_1. or Avia_1.
		name = fragment_name.format(**locals())
		suffix = src_file.split('.')[-1]	
		dst_file = os.path.join(dst_dir, name) + suffix
		start, end = fragment[0:2]

		# import pdb;pdb.set_trace()
		cmd = CMD_TEMPLATE.format(**locals())
		try:
			subprocess.check_call(cmd, shell=True)
		except subprocess.CalledProcessError, e:
			print('Unable to execute the command: %s' % cmd)

		with open(remove_suffix(dst_file)+'.txt', 'w') as f:
			f.write(text)
	return

def guess_mark(src_file):
	name = os.path.basename(src_file)
	r = re.match(IDENTIFIER_PATTERN, name)
	if r:
		identifier = r.group('identifier')
		print('The name to be used for %s is %s' % (src_file, identifier))
		confirm = raw_input('Confirm?(press enter to use the default name)')
		if confirm:
			identifier = confirm
	else:
		print('Unable to match any identifier for %s' % src_file)
		identifier = raw_input('Please specify the name manually:')

	return identifier.capitalize()

def traverse_adaptor(src_file, _):
	fragments = parse(src_file, use_similar=True)
	identifier = guess_mark(src_file)
	dst_dir = os.path.abspath(os.path.join(src_dir, os.path.join(identifier, identifier.lower())))

	# dst_dir = current/dir/Avia/avia
	# fragment_name = identifier+FRAGMENT_NAME_TEMPLATE = Avia_{marker}{index}
	# marker = identifier[0] = A
	generate(src_file, dst_dir, fragments, identifier+FRAGMENT_NAME_TEMPLATE, identifier)

def main():
	# dst_dir = sys.argv[2]
	traverse(src_dir, '', traverse_adaptor, target='.wav')


if __name__ == '__main__':
	src_dir = sys.argv[1]
	main()