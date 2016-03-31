# bash snippets


# to count code lines in total
find ./ -type f | grep -e ".*\.\(py\|sh\)$" | xargs -I % wc -l % | awk 'BEGIN { FS = " "; SUM = 0 }; $2=="total" { SUM += $1 }; END { print SUM }'

find /cygdrive/g/20160222 -name list_all.txt | grep -ie 'task1.*tiger' | xargs -I % cat %| sed 's/ //g' | grep 

for file in `find $1 -type f | grep -e "^clip_\d+\.txt$"`;do
awk 'BEGIN { FS = " "; MANUAL = 0; AUTO = 0 };
    { if ( $9 == "0")
        MANUAL += 1;
      else if ( $9 == "1" )
        AUTO += 1;
      else
        print "unrecognize number ", $9, "in line ", NR;
    }
    END { print FILENAME, "manual: ", MANUAL, ",  auto: ", AUTO}' $file
done