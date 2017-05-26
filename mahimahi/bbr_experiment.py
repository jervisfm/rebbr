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
from bbr_logging import debug_print, debug_print_verbose, stdout_print
from multiprocessing import Process, Queue, Event
from server import run_server
import subprocess


class Flags(object):
    """Dictionary object to store parsed flags."""

    TIME = "time"
    LOSS = "loss"
    PORT = "port"
    CC = "congestion_control"
    RTT = "rtt"
    BW = "bottleneck_bandwidth"
    SIZE = "packet_size"
    HEADLESS = "headless"
    parsed_args = None


def _check_cc(input):
    if input == "bbr" or input == "BBR":
        return "bbr"
    elif input == "cubic" or input == "CUBIC":
        return "cubic"
    else:
        raise argparse.ArgumentTypeError(
            "Choose 'bbr' or 'cubic' as CC: %s" % input)


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
    parser.add_argument('--loss', dest=Flags.LOSS, type=float, nargs=1,
                        help="Loss rate to test (%).",
                        default=0.1)
    parser.add_argument('--port', dest=Flags.PORT, type=int, nargs=1,
                        help="Which port to use.",
                        default=5050)
    parser.add_argument('--cc', dest=Flags.CC, type=_check_cc, nargs=1,
                        help="Which congestion control algorithm to compare.",
                        default="cubic")
    parser.add_argument('--rtt', dest=Flags.RTT, type=int, nargs=1,
                        help="Specify the RTT of the link in milliseconds.",
                        default=100)
    parser.add_argument('--bw', dest=Flags.BW, type=float, nargs=1,
                        help="Specify the bottleneck bandwidth in Mbps.",
                        default=100)
    parser.add_argument('--size', dest=Flags.SIZE, type=int, nargs=1,
                        help="Specify the packet size in bytes.",
                        default=1024)
    parser.add_argument('--headless', dest=Flags.HEADLESS, action='store_true',
                        help="Specify the packet size in bytes.",
                        default=False)

    Flags.parsed_args = vars(parser.parse_args())
    # Preprocess the loss into a percentage
    Flags.parsed_args[Flags.LOSS] = Flags.parsed_args[Flags.LOSS] / 100.0
    debug_print_verbose("Parse: " + str(Flags.parsed_args))


def _run_experiment(loss, port, cong_ctrl):
    """Run a single throughput experiment with the given loss rate."""
    debug_print("Running experiment [loss = " +
                str(loss) + ", cong_ctrl = " + str(cong_ctrl) + "]")

    client_args = "(\'" + str(cong_ctrl) + "\')"

    headless = Flags.parsed_args[Flags.HEADLESS]

    if not headless:
        command = ' '.join(["mm-delay", "50", "mm-loss", "uplink", str(loss),
                            "mm-link", "100Mbps.up", "100Mbps.down", "--meter-uplink", "--once",
                            "--", "python", "-c", "\"from client import run_client; run_client" + client_args + "\""])
        subprocess.check_call(command, shell=True)
    else:
        command = ' '.join(["mm-delay", "50", "mm-loss", "uplink", str(loss),
                            "mm-link", "100Mbps.up", "100Mbps.down", "--once",
                            "--", "python", "-c", "\"from client import run_client; run_client" + client_args + "\""])
        subprocess.check_call(command, shell=True)



def main():
    """Run the experiments."""
    debug_print("Replicating Google BBR Figure 8.")

    # Grab the experimental parameterss
    _parse_args()

    port = Flags.parsed_args[Flags.PORT]
    size = Flags.parsed_args[Flags.SIZE]
    loss = Flags.parsed_args[Flags.LOSS]
    rtt = Flags.parsed_args[Flags.RTT]
    bw = Flags.parsed_args[Flags.BW]
    cc = Flags.parsed_args[Flags.CC]

    # Generate the trace files based on the parameter
    _generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.up")
    _generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.down")

    for cong_ctrl in ['bbr', cc]:
        # Start the client and server
        q = Queue()
        e = Event()
        server_proc = Process(
            target=run_server, args=(q, e, cong_ctrl, port, size))
        server_proc.start()
        client_proc = Process(target=_run_experiment,
                              args=(loss, port, cong_ctrl))
        client_proc.start()
        client_proc.join()          # Wait for the client to finish
        debug_print_verbose("Signal server to shutdown.")
        e.set()  # signal the server to shutdown
        server_proc.join()     # kill the server
        goodput = q.get()
        debug_print_verbose("Run complete. Goodput: " + str(goodput))
        q.close()
        e.clear()
        debug_print("Experiment complete!")

        # Print the output
        results = ', '.join([str(x) for x in [cc, loss, goodput, rtt, bw]])
        stdout_print(results + "\n")

    debug_print("Terminating driver.")


if __name__ == '__main__':
    main()
