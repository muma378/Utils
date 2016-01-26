# bash snippets


# to count code lines in total
find ./ -type f | grep -e ".*\.\(py\|sh\)" | xargs -I % wc -l % > wc.log
awk 'BEGIN { FS = " "; SUM = 0 }; $2=="total" { SUM += $1 }; END { print SUM }' wc.log

