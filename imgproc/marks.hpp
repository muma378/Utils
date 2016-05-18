//
//  marks.h
//  
//
//  Created by Xiao Yang on 16/1/4.
//
//

#ifndef __CVUTILS_MARKS__
#define __CVUTILS_MARKS__

#include "main.hpp"
#include <fstream>
#include <sstream>

vector<Point> &getPositions(const char* positions_file, vector<Point>& positions_points);
vector<string> &split(const string &s, char delim, vector<string> &elems);
vector<string> &split(const string &s, char delim);
void marks(const char* img_file, const char* positions_file, const char* dst_file);

#endif
