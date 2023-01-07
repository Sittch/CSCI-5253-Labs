#!/usr/bin/env python
"""URLMapper.py"""

import sys
import re

# input comes from STDIN (standard input)
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()
    # split the line into words
    words = line.split()
    # increase counters
    for word in words:
        
        # regex = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+'
        # urls = re.findall(regex, word)
        # print(urls)
        
        
        regex = r'href=\"([^<>]*)\"'
        urls = re.findall(regex, word)
        #print(urls)
        
        
        #regex = r'href=\".*\"'
        #urls = re.findall(regex, word)
        #print(urls)
        
        # write the results to STDOUT (standard output);
        # what we output here will be the input for the
        # Reduce step, i.e. the input for reducer.py
        #
        # tab-delimited; the trivial word count is 1
        for url in urls:
            print('%s\t%s' % (url, 1))
