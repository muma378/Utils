# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse

from builder import OperationsBuilder

def validate_args(args):
	target = args.target
	if args.type == 'd':
		if not os.path.isdir(target):
			raise IOError("directory " + target + " is not existed")
	if args.type == 'f':
		if not os.path.isfile(target):
			raise IOError("file " + target + " is not existed")
	return True


def main():
	parser = argparse.ArgumentParser(prog=sys.argv[0], description=u'TextGrid线下质检工具')
	parser.add_argument('--type', default='d', choices=('f', 'd'), help=u"检查的目标类型为文件(f)或文件夹(d)")
	parser.add_argument('-t', '--target', metavar='path', required=True, help=u"目标文件夹或文件")

	# create the interface to sub-command
	subparser = parser.add_subparsers(title=u"子命令", metavar="sub-commands")

	ob = OperationsBuilder()
	verify_parser = subparser.add_parser('verify', help=u"检查并输出非法文本")
	verify_parser.set_defaults(builder=ob.verify)

	time_parser = subparser.add_parser('time', help=u"统计时长")
	time_parser.add_argument('-p', '--print', nargs='+', metavar='not-empty', default=('total', 'not-empty', 'valid'), 
		choices=('total', 'not-empty', 'valid'), help=u"打印类型: total - 目标文件夹内的总时长和有效时长；\nnot-empty - 含有任意标注信息的总时长；\nvalid - 含有合法文本的总时长")
	time_parser.add_argument('-a', '--action', metavar='action', default='separately', choices=('separately', 'together'), 
		help=u"统计动作：separately - 分类统计；\ntogether - 合并统计")
	time_parser.add_argument('-l', '--layer', metavar='N', default=1, type=int, help=u'被统计的层次，例如统计item[3]的时长时，该值为3')
	time_parser.set_defaults(builder=ob.timeit)

	args = parser.parse_args(sys.argv[1:])
	if validate_args(args):
		args.builder(args)
		ob.run()

if __name__ == '__main__':
	main()