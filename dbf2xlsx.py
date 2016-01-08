# -*- coding: utf-8 -*-
import openpyxl as px
from dbfread import DBF

CHECK_FIELDS = ['W15000105', 'W15018103']
# CHECK_COLS = ['U', 'AK']
AVERAGE_FIELDS = ['W19020104', 'W19020102', 'W19020103', 'W19020101', 'W15000105', 'W15018103', 'W15011004', 'W15011005', 'W15011006', 'W15011007', 'W13050002']
# AVERAGE_COLS = ['F', 'G', 'H', 'I', 'U', 'AK', 'AQ', 'AR', 'AS', 'AT', 'CP']
FIELDS_TEXT = {'W19020104': u'土压 下', 'W19020102': u'土压 左', 'W19020103': u'土压 右', 'W19020101': u'土压 上', 'W15000105': u'总推力', 'W15018103': u'刀盘转速', 'W15011004': u'注浆 右上', 'W15011005': u'注浆 右下', 'W15011006': u'注浆 左下', 'W15011007': u'注浆 左上', 'W13050002': u'刀盘扭矩'}
# WORDS_INSERT = {'F': u'土压 下', 'G': u'土压 左', 'H': u'土压 右', 'I': u'土压 上', 'U': u'总推力', 'AK': u'刀盘转速', 'AQ': u'注浆 右上', 'AR': u'注浆 右下', 'AS': u'注浆 左下', 'AT': u'注浆 左上', 'CP': u'刀盘扭矩'}


class InvalidLineException(Exception):
	pass
		


def readfiles(root_dir):
	sep = '\\' if os.name is 'nt' else '/'
	items = {}
	for dirpath, dirnames, filenames in os.walk(root_dir):
		for filename in filenames:
			process(filename)
	return items


# reads dbf and removes unqualified data
def process(filename): 
	with DBF(filename, load=True) as t:
		fields_avg = []
		import pdb;pdb.set_trace()
		# row index and data
		for ri, record in enumerate(t.records):
			try:
				for attr in CHECK_FIELDS:
					if record[attr] == 0:
						t.deleted.append(t.records.pop(ri))
						raise InvalidLineException('Warning: line %d in %s is invalid, has been removed ' % (ri, filename))			
				for fi, avg_attr in enumerate(AVERAGE_FIELDS):
					fields_avg[fi] = record[attr] 
			except InvalidLineException as e:
				print e

		size = float(len(t.records))
		fields_avg = [ v / size for v in fields_avg ]
		gen_xlsx(t.records, filename)
	return fields_avg


def gen_xlsx(xlsx_dict, filename):
	workbook = px.load_workbook(filename)
	sheets = workbook.get_sheet_names()
	for s in sheets:
		ws = workbook[s]
	


if __name__ == '__main__':
	readfiles(sys.argv[1])