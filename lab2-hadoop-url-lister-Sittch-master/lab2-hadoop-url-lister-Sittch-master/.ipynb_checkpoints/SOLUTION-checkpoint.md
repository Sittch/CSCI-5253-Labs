Mitchell Allen
Lab 2: Hadoop URL Lister
9/8/22

My solution reuses the majority of the code from the given
Mapper.py and Reducer.py files to extract URLs from the input text
files. A few small alterations were necessary to change the focus from
words to URLs, including a regex function.

My output matched the intended output posted by the professor, although
they were not produced in the same alphabetical order as the professor's.

The cluster with four workers was actually slightly slower than the cluster
with two workers. Maybe this small difference was due to the relative
quickness of the task overall?

I am not familiar with Java, and I did not implement the Java version, but I think the Java WordCount1 implementation might cause problems and produce a different output due to the Combiner producing key-value collection pairs instead of simply key-value pairs. This could cause the URLs to be counted improperly, leading to an inaccurate final list. The best reference I could find on this was here: https://www.tutorialspoint.com/map_reduce/map_reduce_combiners.htm

I also utilized the professor's documentation, discussions on Piazza, and assistance from Paul
Hoffman to complete the assignment. I ran the script on both the Google Cloud and CSEL Jupyter
Notebooks within the Datacenter Scale Computing setup.