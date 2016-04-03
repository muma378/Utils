#!/bin/bash

if [ $# -lt 3 ];then
    echo "usage: $0 jar-name main.java input [MainJavaClass]"
    exit
fi

JAR_NAME=$1
JAVA_MAIN_CLASS=$2
INPUT=$3

rm *.class
# hadoop library and current dir
JAVA_CLASSPATH=`yarn classpath`:.
javac -classpath ${JAVA_CLASSPATH} -Xlint:deprecation -d . ${JAVA_MAIN_CLASS}
jar cf ${JAR_NAME} *.class

if [ -z $4 ];then
    JAVA_ENTRANCE=`echo ${JAVA_MAIN_CLASS} | sed 's/\(.*\)\.java/\1/'`
else
    JAVA_ENTRANCE=$4
fi

export HADOOP_CLASSPATH=./${JAR_NAME}
$HADOOP_HOME/bin/hadoop ${JAVA_ENTRANCE} ${INPUT} output
