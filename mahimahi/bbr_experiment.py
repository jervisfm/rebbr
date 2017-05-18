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
from bbr_logging import debug_print, debug_print_verbose
import subprocess
import time


class Flags(object):
    """Dictionary object to store parsed flags."""

    TIME = "time"
    LOSS = "loss"
    PORT = "port"

    parsed_args = None


def _read_output(pipe, q):
    """Read output from `pipe`, when line has been read, putsline on Queue `q`."""
    while True:
        l = pipe.readline()
        q.put(l)


def _read_input(write_pipe, in_pipe_name):
    """Read input from a pipe with name `read_pipe_name`, writing this input straight into `write_pipe`."""
    while True:
        with open(in_pipe_name, "r") as f:
            write_pipe.write(f.read())


def _generate_100mpbs_trace(seconds, filename):
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


def _parse_args():
    """Parse experimental parameters from the commandline."""
    parser = argparse.ArgumentParser(
        description="Process experimental params.")
    parser.add_argument('--time', dest=Flags.TIME, type=int, nargs=1,
                        help="Enter a time in seconds to run each trace.",
                        default=20)
    parser.add_argument('--loss', dest=Flags.LOSS, type=float, nargs=argparse.REMAINDER,
                        help="Loss rates to test.",
                        default=[0.001, 0.01, 0.1, 1, 2, 5, 10, 15, 20, 25, 30, 40, 50])
    parser.add_argument('--port', dest=Flags.PORT, type=int, nargs=1,
                        help="Which port to use.",
                        default=5050)

    Flags.parsed_args = vars(parser.parse_args())
    debug_print_verbose("Parse: " + str(Flags.parsed_args))


def _run_experiment(loss, port, cong_ctrl):
    """Run a single throughput experiment with the given loss rate."""
    debug_print("Running experiment [loss = " +
                str(loss) + ",\tcong_ctrl = " + str(cong_ctrl) + "]")

    process = subprocess.Popen(
        ["stdbuf", "-o0", "mm-delay", "50", "mm-loss", "uplink", str(loss),
         "mm-link", "100Mbps.up", "100Mbps.down", "--uplink-log=/tmp/bbr_log",
         "--meter-uplink", "--once", "--", "stdbuf", "-o0", "python",
         "client.py", str(port), str(cong_ctrl)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)

    return process


def _start_server(port, loss, cong_ctrl):
    """Run the Python server."""
    # TODO(luke): add size?
    process = subprocess.Popen(
        ["stdbuf", "-o0", "python", "server.py", str(port), "--loss", str(loss), "--cc", str(cong_ctrl)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    debug_print_verbose("Starting server on port " + str(port))
    return process


def _make_plots(logfile):
    """Generate high quality plots of data."""
    # TODO(luke) generate the plot like figure 8
    return

def main():
    """Run the experiments."""
    debug_print("Replicating Google BBR Figure 8.")
    logfile = './experiment_log.csv'
    with open(logfile, "w"):
        # log.write("cc, loss, goodput\n")
        pass

    # Grab the experimental parameters
    _parse_args()

    # Generate the trace files based on the parameter
    _generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.up")
    _generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.down")

    # queues for storing output lines
    # server_q = Queue.Queue()
    # experiment_q = Queue.Queue()

    loss_rates = Flags.parsed_args[Flags.LOSS]
    port = Flags.parsed_args[Flags.PORT]

    loss_rates = Flags.parsed_args[Flags.LOSS]
    for cong_ctrl in ['cubic', 'bbr']:
        for loss in loss_rates:
            # Start the server
            server_proc = _start_server(port, loss, cong_ctrl)
            client_proc = _run_experiment(loss, port, cong_ctrl)

            while True:
                client_proc.poll()
                if client_proc.returncode is not None:
                    time.sleep(2)  # Give the server time to log the results.
                    server_proc.terminate()
                    break

    debug_print("Experiment complete! Data stored in: " + str(logfile))
    debug_print("Terminating driver.")

    # TODO(luke) Make the graphs from that CSV
    _make_plots(logfile)

if __name__ == '__main__':
    main()
