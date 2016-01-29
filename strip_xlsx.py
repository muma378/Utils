import os
import sys
import openpyxl as px


def readxlsx(filename):
	print("reading xlsx file %s" % filename)
	wb = px.load_workbook(filename=filename)
	for ws in wb:
		for row in ws.rows:
			for cell in row:
				cv = cell.value
				if type(cv) is unicode or type(cv) is str:
					if cv != cv.strip():
						ws[cell.column+str(cell.row)] = cv.strip()

	print("saving now...")
	wb.save("strip_"+os.path.basename(filename))


if __name__ == '__main__':
	readxlsx(sys.argv[1])