# bash snippets
# useful commands in several lines

# to count code lines in total
find ./ -type f | grep -e ".*\.\(py\|sh\|cpp\|h\)$" | xargs -I % wc -l % | awk 'BEGIN { FS = " "; SUM = 0 }; { SUM += $1 }; END { print SUM }'


# count fields separately 
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

# substitute all text files
find ./ -type f -name "*.txt" | xargs -I % sed -i '' -e 's/""/"/g;s/\([^\s]\)\(\[\)/\1 \2/g;s/^1//g' %
