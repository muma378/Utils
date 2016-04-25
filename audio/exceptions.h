//  exceptions.h
//  audio
//
//  Created by Xiao Yang on 16/4/8.
//  Copyright (c) 2016年 Young. All rights reserved.
//

#ifndef audio_exceptions_h
#define audio_exceptions_h

class BaseException: public std::exception
{
private:
    const char* message = nullptr;
    
public:
    BaseException(){};
    BaseException(const char* msg){
        this->message = msg;
    }
    
    virtual const char* what() const throw()
    {
        return message;
    }
};


class UnreadableException: public BaseException
{
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

#endif
