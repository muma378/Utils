import os
import math

# columns' index considered in the computation, starts with 0
INTERESTED_COLS = [0, 1, 2]
# the index of column represents y
Y_COL = 0

# location of the csv file
CSV_FILENAME = '/Users/imac/Downloads/data.csv'
# suffix of csv files
CSV_SUFFIX = 'csv'



# functions to map varibles
# the number before colon means the index of column to be mapped
# the rest is the function, which needs to be written as the following indicates
# functions provided:
# 1. Power and logarithmic functions - exp(x), log(x), log10(x), sqrt(x)
# 2. trigonometric functions - cos(x), sin(x), tan(x), acos(x), asin(x), atan(x)
# 3. 
MAPING_FUNCTIONS = {
	# 1: "f(x) = cos(x)",
	# 2: "f(x) = x^2", 	
}

CUSTOM_FUNCTIONS = {
	'x^2': lambda x: math.pow(x, 2),
	'x^2-1': lambda x: x*x-1,
}