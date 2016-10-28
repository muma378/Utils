# -*- coding: utf-8 -*-
import sys
from traverse import traverse_with_extra
import os

SLOTS_FILENAME = "slots.txt"

def serialize(slots, out):
    for phrase, times in slots.items():
        out.write(phrase)
        out.write("\n")

def fill(srcfile, _, **kwargs):
    with open(srcfile) as f:
        content = f.read()
    content = content.strip()
    if kwargs['slots'].get(content):
        kwargs['slots'][content] += 1
    else:
        kwargs['slots'][content] = 1
    
def deserialize(filename):
    slots = {}
    with open(filename) as f:
        for line in f:
            slots[line.strip()] = 1
    return slots

def collect(dirlist):
    slots = {}
    if os.path.exists(SLOTS_FILENAME):
        slots = deserialize(SLOTS_FILENAME)
    else:
        with open(dirlist) as f:
            for dirname in f:
                dirname = dirname.strip().decode("utf-8")
                if dirname.startswith('#'):
                    continue
                traverse_with_extra(dirname, '', fill, target='.txt', slots=slots)
        with open(SLOTS_FILENAME, "w") as f:
            serialize(slots, f)            
    return slots

if __name__ == '__main__':
    dirlist = sys.argv[1]
    output = sys.argv[2]
    phrases = collect(dirlist)
    with open(output, 'w') as f:
        for key, val in phrases.items():
            f.write(key)
            f.write("\n")
