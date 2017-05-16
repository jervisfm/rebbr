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
from bbr_logging import debug_print, debug_print_error, debug_print_verbose
import subprocess
import sys


class Flags(object):
    """Dictionary object to store parsed flags."""

    TIME = "time"
    LOSS = "loss"

    parsed_args = None


def generate_100mpbs_trace(seconds, filename):
    """Generate a 100Mbps trace that last for the specified time."""
    # TODO(luke): We want this to take in a bandwidth and length and generate
    # the corresponding trace file. We can just use 100Mbps for now.
    debug_print_verbose("Creating " + str(seconds) + " sec Trace: " + filename)
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

    Flags.parsed_args = vars(parser.parse_args())
    debug_print_verbose("Parse: " + str(Flags.parsed_args))


def run_experiment(loss_rate):
    """Run a single throughput experiment with the given loss rate."""
    debug_print("Running experiment with loss of: " + str(loss_rate))
    # cmd1 = ("mm-delay 50")
    # cmd2 = ("ls -a")
    cmd1 = ("mm-delay 50 mm-loss uplink " + str(loss_rate) + " --meter-uplink" +
           "--once 100Mbps.up 100Mbps.down")
    cmd2 = ("./client.py 5050 0")
    process = subprocess.Popen("{}; {}".format(
        cmd1, cmd2), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error:
        debug_print_error(error)

    debug_print(output)


def start_server():
    """Run the Python server."""
    try:
        process = subprocess.Popen("./server.py 5050", shell=True, stdout=subprocess.PIPE)
    except OSError as err:
        debug_print_error(err)
        sys.exit(-1)

    debug_print_verbose("Starting server: " + str(process))
    return process


def main():
    """Run the experiments."""
    debug_print("Replicating Google BBR Figure 8.")

    # Grab the experimental parameters
    parse_args()

    # Generate the trace files based on the parameter
    generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.up")
    generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.down")

    # Start the server
    server_proc = start_server()

    # loss_rates = Flags.parsed_args[Flags.LOSS]
    # for loss in loss_rates:
    #     run_experiment(loss)
    #     break

    server_proc.terminate()  # Kill the server to clean up

if __name__ == '__main__':
    main()
