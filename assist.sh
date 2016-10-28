#!/bin/bash

ENV_ANALYSIS=/Users/imac/Documents/Code/exercises/pyenv/data_analysis_env/bin/activate

source ${ENV_ANALYSIS}
LIB_DP=/Users/imac/Documents/Code/exercises/dp/src
export PYTHONPATH=${LIB_DP}:$PYTHONPATH

python $@

