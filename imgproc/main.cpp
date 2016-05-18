/*  CV_Utils - usage: ./CV_Utils tool_name image ... [-text, -dst]
    An interface to the utilize all tools. 
    Users can get famaliar with all tools and their arguments by typing the option help
    Author: xiao yang <xiaoyang0117@gmail.com>
    Date: 2016.01.04
 */

#include "main.hpp"
#include "contours.hpp"
#include "marks.hpp"
#include <map>

const string basename(const string& path){
    vector<string> elems;
    split(path, '/', elems);
    return elems.back();
}


int main(int argc, char** argv){
    const string keys =
    "{help h usage  |       |usage              }"
    "{@util         |       |the util to call   }"
    "{@img1         |       |the src image      }"
    "{@img2         |<none> |the dst image      }"
    "{dst d         |       |the folder to save }"
    "{text t        |       |text file to refer }"
    "{shape s       |cross  |the shape used to mark }"
    ;
    
    CommandLineParser parser(argc, argv, keys);
    
    if (parser.has("help")) {
        parser.printMessage();
        return 0;
    }
    string util = parser.get<string>(0);
    string img1 = parser.get<string>(1);
    string img2 = parser.get<string>(2);
    
    string dst  = parser.get<string>("dst");
    string txt  = parser.get<string>("text");
    string shape = parser.get<string>("shape");
    
//    util = "marks";
//    img1 = "street-image/ScreenShot/DaTang_Entrance_Windy-00001.bmp";
//    img2 = "street-image/Body/DaTang_Entrance_Windy-00001.bmp";
//    txt = "street-image/Position/DaTang_Entrance_Windy-00001.bmp.txt";
//     dst = "street-image/Marks/"
    
    map<string, int> utils_map = {
        { "contours", 1 },
        { "marks", 2 },
    };
    
    try {
        string dst_file;
        switch (utils_map.at(util)) {
            case 1:
                dst_file = dst + basename(img1);
                contours(img1.c_str(), img2.c_str(),dst_file.c_str());
                break;
            case 2:
                dst_file = dst + basename(img1);
//                marks(img1.c_str(), txt.c_str(), dst_file.c_str(), shape.c_str());
                marks(img1.c_str(), txt.c_str(), dst_file.c_str());
                break;
            default:
                cout << "Does not support this util." << endl;
                exit(0);
        }
    } catch (const out_of_range& oor) {
        parser.printMessage();
        // try a sample
//        contours("street-image-sample/ScreenShot/DaTang_Entrance_Windy-00001.bmp", "street-image-sample/Body/DaTang_Entrance_Windy-00001.bmp", "sample.bmp");
        marks("/Users/imac/Downloads/Xinxi_Road_Fewer_2-00001.bmp", "/Users/imac/Downloads/Xinxi_Road_Fewer_2-00001.bmp.txt", "/Users/imac/Desktop/Xinxi_Road_Fewer_2-00001.bmp");
    }
    
//    contours("street-image-sample/ScreenShot/DaTang_Entrance_Windy-00001.bmp", "street-image-sample/Body/DaTang_Entrance_Windy-00001.bmp");
//    marks("street-image-sample/ScreenShot/DaTang_Entrance_Windy-00001.bmp", "street-image-sample/Position/DaTang_Entrance_Windy-00001.bmp.txt");

}