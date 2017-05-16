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
import Queue
import subprocess
import threading


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


def _run_experiment(loss):
    """Run a single throughput experiment with the given loss rate."""
    debug_print("Running experiment with loss of: " + str(loss))

    # Set up the mahimahi environment
    # cmd1 = ("mm-delay 50 mm-loss uplink " + str(loss) + " --meter-uplink " +
    #         "--once 100Mbps.up 100Mbps.down")
    process = subprocess.Popen(
        ["stdbuf", "-o0", "mm-delay", "50", "mm-loss", "uplink", str(loss),
         "mm-link", "100Mbps.up", "100Mbps.down", "--uplink-log=/tmp/bbr_log",
         "--meter-uplink", "--once"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    return process


def _start_server(port):
    """Run the Python server."""
    process = subprocess.Popen(
        ["stdbuf", "-o0", "python", "server.py", str(port)], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    debug_print_verbose("Starting server: " + str(process))
    return process


def main():
    """Run the experiments."""
    debug_print("Replicating Google BBR Figure 8.")

    # Grab the experimental parameters
    _parse_args()

    # Generate the trace files based on the parameter
    _generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.up")
    _generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.down")

    # queues for storing output lines
    server_q = Queue.Queue()
    experiment_q = Queue.Queue()

    loss_rates = Flags.parsed_args[Flags.LOSS]
    port = Flags.parsed_args[Flags.PORT]
    # Start the server
    server_proc = _start_server(port)

    # start a pair of thread to read output from server
    server_t = threading.Thread(
        target=_read_output, args=(server_proc.stdout, server_q))
    server_t.daemon = True
    server_t.start()

    loss_rates = Flags.parsed_args[Flags.LOSS]
    for loss in loss_rates:
        client_proc = _run_experiment(loss)
        client_proc.stdin.write(
            "stdbuf -o0 python client.py " + str(port) + " cubic" + "\n")

        # start a pair of thread to read output from client
        client_t = threading.Thread(
            target=_read_output, args=(client_proc.stdout, experiment_q))
        client_t.daemon = True
        client_t.start()

        while True:
            client_proc.poll()
            if client_proc.returncode is not None:
                break

            # write output from Server (if there is any)
            try:
                l = server_q.get(False)
                debug_print("           <<< Server" + l)
            except Queue.Empty:
                pass

            # write output from client (if there is any)
            try:
                l = experiment_q.get(False)
                debug_print("Client >>> " + l)
            except Queue.Empty:
                pass

        # TODO(luke): This is leaving a bunch of zombie client processes.
    server_proc.terminate()
    debug_print("Terminating driver.")


if __name__ == '__main__':
    main()
