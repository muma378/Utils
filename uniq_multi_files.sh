#!/bin/bash

MERGEFILE='merge.txt'
UNIQ_MERGEFILE='uniq_merge.txt'
touch $MERGEFILE
echo '' > $MERGEFILE

for i in $@;do
    if [ -e ${i} ];then
        sort $i | uniq | sed "s/.*/${i}  &/" >> $MERGEFILE 
    else
        echo 'Can not find the file '
        echo $i
        exit
    fi
done

sort -k2 $MERGEFILE | uniq -f 1 > $UNIQ_MERGEFILE
        
for i in $@;do
    awk -v filename=${i} '
        BEGIN { FS=" " };
        filename==$1 {$1=""; print $0;};
        ' $UNIQ_MERGEFILE | sed 's/^ //' > ${i}".backup" 
done


