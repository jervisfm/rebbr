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

import argparse
from bbr_logging import debug_print, debug_print_warn, debug_print_error, debug_print_verbose


class Flags(object):
    """Dictionary object to store parsed flags."""

    TIME = "time"
    LOSS = "loss"

    parsed_args = None


def generate_100mpbs_trace(seconds, filename):
    """Generate a 100Mbps trace that last for the specified time."""
    # TODO(luke): We want this to take in a bandwidth and length and generate
    # the corresponding trace file. We can just use 100Mbps for now.
    with open(filename, 'w') as outfile:
        for ms_counter in range(int(seconds * 1000)):
            if (ms_counter % 3 == 0):
                for j in range(9):
                    outfile.write(str(ms_counter + 1) + '\n')
            else:
                for j in range(8):
                    outfile.write(str(ms_counter + 1) + '\n')


def parse_args():
    """Parse experimental parameters from the commandline."""
    parser = argparse.ArgumentParser(
        description="Process experimental params.")
    parser.add_argument('--time', dest=Flags.TIME, type=int, nargs=1,
                        help="Enter a time in seconds to run each trace.",
                        default=20)
    parser.add_argument('--loss', dest=Flags.LOSS, type=float, nargs=argparse.REMAINDER,
                        help="Loss rates to test.",
                        default=[0.001, 0.01, 0.1, 1, 2, 5, 10, 15, 20, 25, 30, 40, 50])

    Flags.parsed_args = parser.parse_args()
    debug_print_verbose("Parse: " + str(Flags.parsed_args))


def main():
    """Run the experiments."""
    debug_print("Replicating Google BBR Figure 8.")

    # Grab the experimental parameters
    parse_args()

    # Generate the trace files based on the parameter
    generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.up")
    generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.down")

if __name__ == '__main__':
    main()
