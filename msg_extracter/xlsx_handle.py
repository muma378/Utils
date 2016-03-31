# -*- coding: utf-8 -*-
# xlsx_handle.py - usage: xh = XlsxHandler() 
# wrapper for xlsxwriter and xlrd
# authors: liu size, xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.22
import xlsxwriter
import xlrd
import os

class XlsxHandler(object):
    def read_file(self, filename):
        if not os.path.isfile(filename):
            print 'file path error!'
        else:
            self.databook = xlrd.open_workbook(filename)
            self.datasheet = self.databook.sheet_names()
            table = self.databook.sheet_by_index(0)
            nrows = table.nrows
            ncols = table.ncols
            for i in xrange(nrows):
                yield table.row_values(i)
    
    def create_excel(self, filename):
        self.workbook = xlsxwriter.Workbook(filename)
        self.worksheet = self.workbook.add_worksheet()

    def set_work_sheet(self, format_dict):
        try:
            self.header_bg_color = format_dict['bg_color']
            self.sheet_long = format_dict['sheet_long']
            self.sheet_hight = format_dict['sheet_hight']
            '''And More'''
        except KeyError as e:
            print '[set_work_sheet]:' + str(e)
        
    def set_excel_headers(self, set_format, headers):
        bold = self.workbook.add_format(set_format)
        bold.set_align('center')
        bold.set_align('vcenter')
        bold.set_bold(True)
        bold.set_pattern(1)
        bold.set_bg_color(self.header_bg_color)
    
        for item in headers:
             if len(set(item[0].split(':'))) > 1:
                self.worksheet.set_column(item[0],item[2]) #设置每行长度
                self.worksheet.merge_range(item[0],item[1],bold)
             else:
                self.worksheet.set_column(item[0],item[2]) #设置每行长度
                self.worksheet.write(item[0].split(":")[0],item[1],bold)
                

    def write_to_excel(self, rows, cols, data):
        bold = self.workbook.add_format({})
        bold.set_align('vcenter')
        #self.worksheet.set_column(rows,cols,self.sheet_long)
        self.worksheet.set_row(rows, self.sheet_hight)
        self.worksheet.write(rows, cols, data, bold)
