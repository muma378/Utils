#!/bin/sh
# TimeFormatter.sh - usage: ./TimeFormatter.sh <dir_name>
# find all text files under the directory dir_name and format the time fields
# to convert them into the format of seconds only
# auther: xiao yang <xiaoyang0117@gmail.com>
# date: 2015.12.25


DIRNAME=$1
TEMPFILE="temp.txt"

if [ ! -e $TEMPFILE ]
then 
    touch $TEMPFILE 
else
    echo "" > $TEMPFILE
fi

function awk_format {
awk '
BEGIN { CONVFMT="%.3f"; }
{
    for(i=1;i<=NF;i++){ 
        if($i~/^[0-9]+:[0-9]+:[0-9|.]+/){
            hours=$i;
            sub(/:[0-9]+:[0-9|.]+/, "", hours);
            minutes=$i;
            sub(/:[0-9|.]+$/, "", minutes);
            sub(/^[0-9]+/, "", minutes);
            seconds=$i;
            sub(/^[0-9]+:[0-9]+:/, "", seconds);
            $i=(hours+0)*3600.0+(minutes+0)*60+(seconds+0);
        }
        else{
            if($i~/^[0-9]+:[0-9|.]+$/){
            minutes=$i;
            sub(/:[0-9|.]+/, "", minutes);
            seconds=$i;
            sub(/^[0-9]+:/, "", seconds);
            $i=(minutes+0)*60+(seconds+0.0);
            }
        }
        if($i~/^[0-9]+$/){
            $i=$i ".000"
        }
    }
    print $0
}
END {}
' $1 > $TEMPFILE 
cat $TEMPFILE > $1
}

for filename in ` find $DIRNAME  -type f -regex ".*\.txt$"`;do
    echo $filename
    awk_format $filename
done
