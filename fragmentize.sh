#!/bin/bash

FILENAME=$1
NUM=$2

if [ -z $3 ];then
    LINES=200
else
    LINES=$3
fi

for i in `seq 1 ${NUM}`;do
    start=$(($i * $LINES))
    sed -n ${start},$(($start + $LINES - 1))p ${FILENAME} > out_${i}.txt
done
