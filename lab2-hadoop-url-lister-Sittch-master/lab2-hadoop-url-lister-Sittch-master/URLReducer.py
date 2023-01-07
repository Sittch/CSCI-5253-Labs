#!/usr/bin/env python
"""URLReducer.py"""

from operator import itemgetter
import sys
import re

current_URL = None
current_count = 0
URL = None

# input comes from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()

    # parse the input we got from mapper.py
    URL, count = line.split('\t', 1)

    # convert count (currently a string) to int
    try:
        count = int(count)
    except ValueError:
        # count was not a number, so silently
        # ignore/discard this line
        continue

    # this IF-switch only works because Hadoop sorts map output
    # by key (here: word) before it is passed to the reducer
    if current_URL == URL:
        current_count += count
    else:
        if current_URL and current_count > 5:
            # write result to STDOUT
            print('%s\t%s' % (current_URL, current_count))
        current_count = count
        current_URL = URL
            

# do not forget to output the last URL if needed!
if current_URL == URL and current_count > 5:
    print('%s\t%s' % (current_URL, current_count))