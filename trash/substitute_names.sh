#!/bin/sh
#./substitute.sh <dir_path>

ROOT_DIR=$1

function get_filelist {
    local regexp='.*\.'$2
    filelist=(`find $1 -type f -regex $regexp`)
}

get_filelist $ROOT_DIR 'txt'
#echo ${filelist[*]}
for file in ${filelist[@]};do
    echo ${file}
    base_dir=`dirname ${file}`
    # remove blank and line within names
    # sed -i '' "s/^(\s+\n)+$//g;s/.*\.pcm//g" ${file}
    # get_filelist $base_dir 'pcm'
    pcm_names=`find $base_dir -type f -regex '.*\.pcm' | xargs -I % basename % | tr '\n' '\t'`
    # sed -i '' "s:^$:${pcm_names}:" ${file}
    perl -i -pe "s/.*\.pcm.*//g;s:^$:${pcm_names}:" ${file}
done
