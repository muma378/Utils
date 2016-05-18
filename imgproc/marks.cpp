//
//  marks.cpp - usage: CV_Utils marks image.bmp -t positions.txt
//  to mark the positions described in the text file on the image
//  note that rectangles mean the position of heads, and stars mean the position of feet
//
//  Created by Xiao Yang on 16/1/4.
//

#include "marks.hpp"


vector<string> &split(const string &s, char delim, vector<string> &elems){
    stringstream ss(s);
    string item;
    while (getline(ss, item, delim)) {
        elems.push_back(item);
    }
    return elems;
}

vector<string> &split(const string &s, char delim){
    vector<string> elems;
    split(s, delim, elems);
    return elems;
}


// extract last 3 strings of coordination, split each by the delim and construct points' vector by pairs of them
vector<Point> &reconstruct(vector<string> &elems, vector<Point> &points, int gap = 1){
    unsigned long size = elems.size();
    string coord;
    Point point;
    for (int last = 3; last > 0; last--) {
        coord = elems.at(size-last);
        string::size_type idx;
        point.x = int(stof(coord, &idx));
        point.y = int(stof(coord.substr(idx+gap)));
        points.push_back(point);
    }
    return points;
}

// extract each pair of coordinations
// written like "599.99999,402	1170,820"
vector<Point> &construct(vector<string> &elems, vector<Point> &points, int gap = 1){
    unsigned long size = elems.size();
    string coord;
    Point point;
    for (int i = 0; i < size; i++) {
        coord = elems.at(i);
        string::size_type idx;
        point.x = int(stof(coord, &idx));
        point.y = int(stof(coord.substr(idx+gap)));
        points.push_back(point);
    }
    return points;
}

void drawCross(Mat& img, Point p, const Scalar& color, int radius=5, int thickness=3){
    int x = p.x;
    int y = p.y;
    circle(img, p, 2, color, -1);   // draw a dot
//    line(img, Point(x-radius, y), Point(x+radius, y), color, thickness);
//    line(img, Point(x, y+radius), Point(x, y-radius), color, thickness);

}

void drawMarkers(Mat& img, vector<Point> &points){
    const Scalar red(0, 0, 255);
    int thickness = 2;
    int radius = 8;
    for (int i=0; i<points.size(); i+=2) {
        rectangle(img, points.at(i), points.at(i+1), red, thickness);
        drawCross(img, points.at(i+2), red, radius, thickness);
    }
    
}


vector<Point> &getPositions(const char* positions_file, vector<Point>& positions_points){
    vector<string> positions_str;
    Point point;
    
    ifstream positions_fd(positions_file);
    string line;
    while (getline(positions_fd, line)){
        split(line, '\t', positions_str);
        reconstruct(positions_str, positions_points);
//        construct(positions_str, positions_points);

    }
//    for_each(positions_str.begin(), positions_str.end(), [](string& s){ cout << s; });
    return positions_points;
}

void marks(const char* img_file, const char* positions_file, const char* dst_file){
    vector<Point> points;
    Mat img = imread(img_file, IMREAD_COLOR);
    if (img.empty()) {
        cout << "Can not find the image " << img_file << endl;
        return;
    }
    getPositions(positions_file, points);
    drawMarkers(img, points);
    imwrite(dst_file, img);
}

