#!/bin/bash
# uniq_multi_files.sh - usage: ./uniq_multi_files.sh file1 file2 ...
# to make the lines within the files unique, remove repeated lines in the latter file
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2015.12.29

MERGEFILE='merge.txt'
UNIQ_MERGEFILE='uniq_merge.txt'
touch $MERGEFILE
echo '' > $MERGEFILE

# unique lines in each file, identify each with a number and merge files into one
for i in $@;do
    if [ -e ${i} ];then
        sed '/^$/d' ${i} | sort | uniq | sed "s/.*/${i}  &/" >> $MERGEFILE 
    else
        echo 'Unable to find the file '
        echo $i
        exit
    fi
done

# unique lines in the merged file
# sort as the second field and uniq with ignoring the first field
sort -k2 $MERGEFILE | uniq -f 1 > $UNIQ_MERGEFILE
        
# output respectively
for i in $@;do
    awk -v filename=${i} '
        BEGIN { FS=" " };
        filename==$1 {$1=""; print $0;};
        ' $UNIQ_MERGEFILE | sed 's/^ //' > ${i}".uniq" 
done


