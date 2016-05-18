//
//  borders.cpp - usage: CV_Utils contours src.bmp mask.bmp
//  to extract the contours in mask and depict them at the src file
//
//  Created by Xiao Yang on 16/1/2.
//
//

#include "contours.hpp"


/*
 TODO: use k-means to find the 3 main colors and then extract contours 
 by using different thresholds, at last apply these contours to the src
 */

void help(){
    cout << "contours";
}

Rect& getDiagnoalPoints(vector<Point>& contour, Rect& diag){
    vector<Point>::iterator it = contour.begin();
    // get points for left-up and right-down in the new rectangle
    Point lu(*it);  // smallest
    Point rd(*it);  // largest
    for ( it += 1 ; it != contour.end(); ++it) {
        lu.x = min(lu.x, it->x);
        lu.y = min(lu.y, it->y);
        
        rd.x = max(rd.x, it->x);
        rd.y = max(rd.y, it->y);
    }
    diag = Rect(lu, rd);
    return diag;
    
}


Mat& drawRectangle(Mat& src, vector<vector<Point>>& contours, vector<Vec4i>& hierarchy, const Scalar clr){
    // draw a rectangle according to contours on src
    
    vector<Rect> rectangles;
    Rect diag;
    for (int i = 0; i != -1; i = hierarchy[i][0]) {
        rectangles.push_back(getDiagnoalPoints(contours[i], diag));
    }
    
    for (vector<Rect>::iterator it = rectangles.begin() ; it != rectangles.end() ;  ++it ) {
        rectangle(src,  *it, clr, 2);
    }
    return src;
    
}


// use the built-in functions - findContours and drawContours to extract contours displayed in the "mask"
// and draws the contours in the "src"
void depictContours(Mat& src, Mat& mask){
    vector<vector<Point>> contours;
    vector<Vec4i> hierarchy;
    int ksize = 3;
    
    GaussianBlur(mask, mask, Size(ksize, ksize), 0);
    cvtColor(mask, mask, COLOR_RGB2GRAY);
    findContours(mask, contours, hierarchy, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);
    
    const Scalar green(255, 0, 255);
    drawRectangle(src, contours, hierarchy, green);
    const Scalar yellow(128, 255, 255);
    drawContours(src, contours, -1, yellow, 2, LINE_AA, hierarchy);
   
}

void contours(const char* src_file, const char* mask_file, const char* dst_file){
    Mat src = imread(src_file, IMREAD_COLOR);
    Mat mask = imread(mask_file, IMREAD_COLOR);
    if (src.empty()) {
        cout << "Can not find the image " << src_file << endl;
        return;
    }
    if (mask.empty()) {
        cout << "Can not find the image " << mask_file << endl;
        return;
    }
    
    depictContours(src, mask);
    imwrite(dst_file, src);
}
