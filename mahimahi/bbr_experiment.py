#!/usr/bin/python
"""Main driver of the experiment to replicate BBR Figure 8.

This code accepts experimental parameters as commandline arguments:
    - RTT
    - Loss Rates to try as [min, max, interval]
    - Link Bandwidth
    - Length of the trace
where the default values are the values used in the BBR paper. Then, we
run the experiments using hte specified parameters, log the results, and
create the corresponding figures.
"""


def generate_100mpbs_trace(seconds):
    """Generate a 100Mbps trace that last for the specified time."""
    # TODO(luke): We want this to take in a bandwidth and length and generate
    # the corresponding trace file. We can just use 100Mbps for now.
    with open('100Mbps.up', 'w') as outfile:
        for ms_counter in range(int(seconds * 1000)):
            if (ms_counter % 3 == 0):
                for j in range(9):
                    outfile.write(str(ms_counter + 1) + '\n')
            else:
                for j in range(8):
                    outfile.write(str(ms_counter + 1) + '\n')
