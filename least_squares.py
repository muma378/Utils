import os
import sys
import re
import csv
import copy
import math
import numpy as np
# import matplotlib.pyplot as plt

TITLE = []

try:
	import math_settings as ms
except ImportError, e:
	print("Error: unable to find the settings.py in current file")
	sys.exit(1)


# retrieve specified columns in the csvfile
def retrive_data(filename, columns):
	global TITLE
	if not filename.endswith(ms.CSV_SUFFIX):
		print("Warning: specified filename is detected not ending with 'csv', please check if it has a correct format")
	
	data = []
	with open(filename, 'rb') as csvfile:
		data_reader = csv.reader(csvfile, delimiter=',')
		titles = next(data_reader)
		TITLE = [ titles[i] for i in columns ]
		for row in data_reader:
			data.append([ float(row[i]) for i in columns ])
	return data

def fns_interpret(maping_fn):
	FN_NAME_PATTERN = '(?P<fn>\w+)\(x\)$'
	FN_DEFINITION_PATTERN = '^( *f\(x\) *= *)?(?P<def>.+?) *$'

	# try to remove the header part, which is 'f(x) = '
	try:
		definition = re.search(FN_DEFINITION_PATTERN, maping_fn).group('def')
	except AttributeError, e:
		definition = maping_fn

	# try to extract the funtion name, such as cos, sin, etc.
	try:
		fn_name = re.search(FN_NAME_PATTERN, definition).group('fn')
	except AttributeError, e:
		fn_name = definition
	

	try:
		fn = vars(math).get(fn_name)
		if not fn:
			fn = ms.CUSTOM_FUNCTIONS[fn_name]
		return fn
	except KeyError, e:
		print("Error: unable to find functions for %s" % fn_name)
		print("please check the documentation for math modul or specify the implementation at 'CUSTOM_FUNCTIONS' field")
		sys.exit(1)
	

def maping(data, dims, fns):

	if dims != len(fns):
		print("Error: the number of functions and variables are not matched ")
		sys.exit(1)

	# assume the mat has the same number of elements in each row
	def transpose(mat):
		T = [ [] for i in range(dims) ]
		for row in mat:
			for i, l in enumerate(T):
				l.append(row[i])
		return T

	trans_data = transpose(data)
	mapped_data = []
	for i, row in enumerate(trans_data):
		mapped_data.append(map(fns[i], row))
	return mapped_data


def compute(data):
	y_array = np.array(data.pop(ms.Y_COL))
	alpha_array = np.ones((1, len(y_array)))
	mat = np.vstack((alpha_array, np.array(data)))

	# core
	coefficient = np.dot(np.linalg.inv(mat.dot(mat.T)), mat.dot(y_array.T))
	return coefficient

def fit_test(coefficient, data):
	data_b = copy.copy(data)

	y_real = np.array(data_b.pop(ms.Y_COL))
	x_real = np.vstack((np.ones(len(y_real)), np.array(data_b)))
	y_est = x_real.T.dot(coefficient)

	ess = np.sum(np.square(y_real-y_est))
	rss = np.sum(np.square(y_est-np.average(y_real)))
	tss = ess + rss

	N = len(y_real)		# observasitions number
	K = len(data) - 1	# 

	global TITLE
	std_err = np.sqrt(np.linalg.inv(x_real.dot(x_real.T))*(ess/(N-K-1))).diagonal()
	variables = [
		("Variables", TITLE),
		("Coefficient", coefficient.astype('str')),
		("Std. Error", std_err.astype('str')),
		("T-statics", (coefficient/std_err).astype('str')),
	]
	for key, vals in variables:
		print("%s\t\t:%s" % (key, '  '.join(vals)))
	
	fit_description = {
		'R-squared         ': rss/tss,
		'Adjsuted R-squared': 1-((ess/tss)*(N-1)/(N-K-1)),
		'S.E. of regression': math.sqrt(ess/(N-K-1)),
		'S.D. dependent var': math.sqrt(tss/(N-1)),
		'Sum squared residua': ess,
		'Mean dependent var': np.mean(y_real),
		'F-statics         ': (rss/2)/(ess/(N-K-1)),
	}

	for key, val in fit_description.items():
		print("%s\t\t:%f" % (key, val))
	print("Processing Finished")

def main():
	try:
		columns = ms.INTERESTED_COLS
		filepath = ms.CSV_FILENAME
		maping_fns = ms.MAPING_FUNCTIONS
	except AttributeError, e:
		print('Error: unable to find the variable in settings.py')
		print(e)

	filename = sys.argv[1] if len(sys.argv) == 2 else filepath
	data = retrive_data(filename, columns)

	fns = []
	for col in columns:
		try:
			fn_str = maping_fns[col]
			fn = fns_interpret(fn_str)
		except KeyError, e:
			fn = lambda x: x
		fns.append(fn)

	mapped_data = maping(data, len(columns), fns)
	coefficient = compute(copy.copy(mapped_data))
	fit_test(coefficient, copy.copy(mapped_data))


if __name__ == '__main__':
	main()