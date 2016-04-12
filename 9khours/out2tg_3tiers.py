# -*- coding: utf-8 -*-
# out2textgrid.py - usage: python out2textgrid.py filelist.out pcmlist.out
# convert files genrated by computeLength.exe to textgrid (3 tiers)	
# author: Zhao Wenjian, Xiao Yang <xiaoyang0117@gmail.com>
# date: 2016.April.12

import os
import sys
import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

TEMPLATE_HEADER = """File type = "ooTextFile"
Object class = "TextGrid"

xmin = {global_xmin}
xmax = {global_xmax}
tiers? <exists>
size = {items_size}
item []:
"""

TEMPLATE_ITEM = """	item [{item_index}]:
		class = "IntervalTier"
		name = "{name}"
		xmin = {global_xmin}
		xmax = {global_xmax}
		intervals: size = {intervals_size}
"""

TEMPLATE_INTERVALS = """			intervals [{interval_index}]:
			xmin = {local_xmin}
			xmax = {local_xmax}
			text = "{text}"
"""

TIERS_NAMES = ["GLOBAL", "SPEAKER", "CONTENT"]

def out2grid(outfile,maxtimedict,outdfile):
	#得到最大shijian
	#print os.path.basename(outfile).split('.')[0]
	maxtime = maxtimedict.get(os.path.basename(outfile).split('.')[0])
	if not maxtime:
		print 'error file : '+outfile
	else:
		#得到输出的开始时间和结束时间列表
		timelist = []
		for line in open(outfile,'r').readlines():
			starttime = float(line.split('->')[0].split('_')[-1].split('.')[0])/1000
			endtime = starttime+float(line.split('->')[-1].strip())
			timelist.append([starttime,endtime])
		timelist.sort()
		#填充列表中静音时段
		before = 0
		outlist = []
		for line in timelist:
			outlist.append([before,line[0]])
			outlist.append([line[0],line[1]])
			before = line[1]

		#写文件
		#outname = str(os.path.basename(outfile).split('.')[0])+str('.TextGrid')
		#outfp = codecs.open(outname,'w','utf_16_be')
		outfp = codecs.open(outdfile,'w','utf_16_be')
		outfp.write('\xef\xbb\xbf')
		
		global_xmin = 0
		global_xmax = maxtime
		# 3 tiers
		outfp.write(TEMPLATE_HEADER.format(items_size=3, **locals()))
		# first tier for GLOBAL
		outfp.write(TEMPLATE_ITEM.format(item_index=1, intervals_size=1, name=TIERS_NAMES[0], **locals()))
		outfp.write(TEMPLATE_INTERVALS.format(interval_index=1, local_xmin=global_xmin, local_xmax=global_xmax, text=""))

		outlist = validate(outlist, maxtime, outfile)
		# second tier for SPEAKER
		outfp.write(TEMPLATE_ITEM.format(item_index=2, intervals_size=len(outlist), name=TIERS_NAMES[1], **locals()))
		write_empty_intervals(outfp, outlist)
		# third tier for CONTENT
		outfp.write(TEMPLATE_ITEM.format(item_index=3, intervals_size=len(outlist), name=TIERS_NAMES[2], **locals()))
		write_empty_intervals(outfp, outlist)
		
		outfp.close()
		

# output  
def write_empty_intervals(fp, outlist, text=''):
	for interval_index, (local_xmin, local_xmax) in enumerate(outlist, start=1):
		fp.write(TEMPLATE_INTERVALS.format(**locals()))


# outlist is a list of pair which has 2 elements stands for the start and end respectively
def validate(outlist, maxtime, outfile):
	index = 1
	for i, line in enumerate(outlist):
		if line[0]>line[1]:		# if the end time bigger than the start
			outlist.remove(line)	# remove it 
			print "value of start is bigger than end at line " + str(i) + " in " + outfile

	outlist.sort()

	if outlist[0][1] == 0:
		del outlist[0]
	if outlist[-1][1] != maxtime:
		outlist[-1][1] = maxtime

	return outlist


#得到么个文件对应的最大时间
def getmaxtime(maxtimefile):
	maxtimedict = {}
	for line in open(maxtimefile,'r').readlines():
		maxtimedict.setdefault(line.split('->')[0].split('\\')[-1].split('.')[0].decode('utf-8').encode('gb2312'),line.split('->')[-1].strip().decode('utf-8').encode('gb2312'))
	return maxtimedict

def cutfile(sourcefile,maxtimedict):
	outkey = {}
	for line in open(sourcefile,'r').readlines():
		key = line.split('->')[0].split('\\')[-2]
		if not outkey.has_key(key):
			outlist = []
			outlist.append(line)
			outkey.setdefault(key,outlist)
		else:
			outlist = outkey[key]
			outlist.append(line)
			outkey.setdefault(key,outlist)

	outfilelist = []
	for key in outkey:
		outfile = codecs.open(os.path.join(os.path.dirname(sourcefile).decode('utf-8').encode('gb2312'),str(key).decode('utf-8').encode('gb2312')+str('.txt.out').decode('utf-8').encode('gb2312')),'w','utf-8')
		outlist = outkey[key]
		for line in outlist:
			outfile.write(line)
		outfile.close()
		print os.path.join(os.path.dirname(sourcefile).decode('utf-8').encode('gb2312'),str(key).decode('utf-8').encode('gb2312')+str('.txt.out').decode('utf-8').encode('gb2312'))
		outfilelist.append(os.path.join(os.path.dirname(sourcefile).decode('utf-8').encode('gb2312'),str(key).decode('utf-8').encode('gb2312')+str('.txt.out').decode('utf-8').encode('gb2312')))


	for line in outfilelist:
		out2grid(line,maxtimedict,line.split('.')[0]+'.TextGrid')


if __name__ == '__main__':

	maxtimedict=getmaxtime(sys.argv[1])
	#out2grid(sys.argv[2],maxtimedict,sys.argv[3])
	cutfile(sys.argv[2],maxtimedict)
	
	# maxtimedict=getmaxtime(r'C:\Users\wenjian\Desktop\20151224\晴晴\original.txt(1).out'.decode('utf-8').encode('gb2312'))
	# out2grid(r'C:\Users\wenjian\Desktop\20151224\晴晴\1.txt.out'.decode('utf-8').encode('gb2312'),maxtimedict)
	
