//  exceptions.h
//  audio
//
//  Created by Xiao Yang on 16/4/8.
//  Copyright (c) 2016年 Young. All rights reserved.
//

#ifndef audio_exceptions_h
#define audio_exceptions_h
#include <string>
#include <cstring>

class BaseException: public std::exception
{
private:
    const char* message = "";
    
public:
    BaseException(){};
    BaseException(const char* msg){
        this->message = msg;
    }
	/*BaseException(std::string & msg) {
		char* c_msg = new char[msg.size() + 1];
		strncpy(c_msg, msg.c_str(), msg.size());
		this->message = c_msg;
		this->message = msg.c_str();
	}*/
    
    virtual const char* what() const throw()
    {
        return message;
    }
};


class UnreadableException: public BaseException{
private:
    const char* message = "Unable to read the audio file";

public:
    using BaseException::BaseException;
    using BaseException::what;
};


class UnwritableException: public BaseException{
private:
    const char* message = "Unable to write the audio file";
    
public:
    using BaseException::BaseException;
    using BaseException::what;
};


class InvalidOperation: public BaseException {
private:
    const char* message = "operation is invalid";

public:
    using BaseException::BaseException;
    using BaseException::what;
};
#endif
