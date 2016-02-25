# bash snippets


# to count code lines in total
find ./ -type f | grep -e ".*\.\(py\|sh\)$" | xargs -I % wc -l % | awk 'BEGIN { FS = " "; SUM = 0 }; $2=="total" { SUM += $1 }; END { print SUM }'

find /cygdrive/g/20160222 -name list_all.txt | grep -ie 'task1.*tiger' | xargs -I % cat %| sed 's/ //g' | grep 