#!/bin/bash
# CompileCVFiles - usage: ./CompileCVFiles prog.cpp image.jpg
# to generate the CMakeLists.txt automatically, and then compile and run the program if exec is 'r'
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2015.03.01

FILE=$1
EXE=${FILE%.cpp}
IMAGE=$2
EXEC=$3
cmakelists="cmake_minimum_required(VERSION 3.1)\n\
project( DisplayImage )\n\
find_package( OpenCV REQUIRED )\n\
set(HAVE_FFMPEG 1)\n\
add_executable( ${EXE} ${FILE} )\n\
target_link_libraries( ${EXE} \${OpenCV_LIBS} )"

if [ -f "${FILE}" ];then
  echo -e $cmakelists > CMakeLists.txt
  make;
else
  echo "ERROR: file ${FILE} doesn't exist."
fi

if [ $# -eq 4 ] && [ $EXEC="r" ];then
  if [ -f "${IMAGE}" ];then
    ./$EXE $IMAGE
  else
    echo "ERROR: file ${IMAGE} doesn't exist."
  fi
fi
