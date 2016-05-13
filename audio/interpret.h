//
//  interpret.h
//  
//
//  Created by Xiao Yang on 16/4/15.
//
//

#ifndef ____interpret__
#define ____interpret__

#include <iostream>
#include "common.h"

template <class T>
class Interpreter {
    T* content;
    
public:
    Interpreter();
};


class BaseInterpreter {

protected:
    char* content;
    uint size;
    
public:
    virtual void say(){
        std::cout << "base class" << std::endl;
    }
};



#endif /* defined(____interpret__) */
