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
from bbr_logging import debug_print, debug_print_verbose, debug_print_error
import csv
import matplotlib
from matplotlib import pyplot as plt
import subprocess
import time


class Flags(object):
    """Dictionary object to store parsed flags."""

    TIME = "time"
    LOSS = "loss"
    PORT = "port"
    CC = "congestion_control"
    RTT = "rtt"
    BW = "bottleneck_bandwidth"

    parsed_args = None


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
                        default=0.01)
    parser.add_argument('--port', dest=Flags.PORT, type=int, nargs=1,
                        help="Which port to use.",
                        default=5050)
    parser.add_argument('--cc', dest=Flags.CC, type=str, nargs=1,
                        help="Which congestion control algorithm to compare.",
                        default="cubic")
    parser.add_argument('--rtt', dest=Flags.RTT, type=int, nargs=1,
                        help="Specify the RTT of the link in milliseconds.",
                        default=100)
    parser.add_argument('--bw', dest=Flags.BW, type=float, nargs=1,
                        help="Specify the bottleneck bandwidth in Mbps.",
                        default=100)

    Flags.parsed_args = vars(parser.parse_args())
    # Preprocess the loss into a percentage
    Flags.parsed_args[Flags.LOSS] = Flags.parsed_args[Flags.LOSS][0] / 100.0
    debug_print_verbose("Parse: " + str(Flags.parsed_args))


def _run_experiment(loss, port, cong_ctrl, display=True):
    """Run a single throughput experiment with the given loss rate."""
    debug_print("Running experiment [loss = " +
                str(loss) + ", cong_ctrl = " + str(cong_ctrl) + "]")

    if display:
        process = subprocess.Popen(
            ["stdbuf", "-o0", "mm-delay", "50", "mm-loss", "uplink", str(loss),
             "mm-link", "100Mbps.up", "100Mbps.down", "--uplink-log=/tmp/bbr_log",
             "--meter-uplink", "--once", "--", "stdbuf", "-o0", "python",
             "client.py", str(port), str(cong_ctrl)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
    else:
        # If display is False, don't show it. This is used for headless operation.
        process = subprocess.Popen(
            ["stdbuf", "-o0", "mm-delay", "50", "mm-loss", "uplink", str(loss),
             "mm-link", "100Mbps.up", "100Mbps.down", "--uplink-log=/tmp/bbr_log",
             "--once", "--", "stdbuf", "-o0", "python",
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
    """Generate high quality plots of data.

    The logfile is a CSV of the format [congestion_control, loss_rate, goodput]
    """
    cubic = {"loss": [], "goodput": []}
    bbr = {"loss": [], "goodput": []}
    xmark_ticks = []

    # For available options on plot() method, see: https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot
    # We prefer to use explicit keyword syntax to help code readability.

    # Create a figure.
    fig_width = 8
    fig_height = 5
    fig, axes = plt.subplots(figsize=(fig_width, fig_height))

    # Add a subplot for CUBIC/BBR plots. See
    # https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.subplot
    # bbr_fig = fig.add_subplot(111)
    # cubic_fig = fig.add_subplot(111)

    with open(logfile, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        reader.next()  # skip header row
        for (cc, loss, goodput) in reader:
            loss_percent = float(loss) * 100
            xmark_ticks.append(loss_percent)

            if cc == 'cubic':
                cubic['loss'].append(loss_percent)
                cubic['goodput'].append(goodput)
            elif cc == 'bbr':
                bbr['loss'].append(loss_percent)
                bbr['goodput'].append(goodput)

            else:
                debug_print_error("This shouldn't happen.")
    debug_print_verbose("CUBIC: %s" % cubic)
    debug_print_verbose("BBR: %s" % bbr)

    matplotlib.rcParams.update({'figure.autolayout': True})

    plt.plot(cubic['loss'], cubic['goodput'], color='blue', linestyle='solid', marker='o',
             markersize=7, label='CUBIC')

    plt.plot(bbr['loss'], bbr['goodput'], color='red', linestyle='solid', marker='x',
             markersize=7, label='BBR')

    plt.xscale('log')

    xmark_ticks = sorted([x for x in set(xmark_ticks)])  # deduplicate
    xmark_ticks.remove(25.0)
    xmark_ticks.remove(15.0)
    xmark_ticks.remove(40.0)

    # For each loss percent, set a mark on x-axis.
    axes.set_xticks(xmark_ticks)

    # Make the X-Axis label look vertical to make them more readable.
    axes.set_xticklabels(axes.xaxis.get_majorticklabels(),
                         rotation=90, fontsize=14)

    # Format the Y-Axis too
    axes.set_yticklabels(axes.yaxis.get_majorticklabels(), fontsize=14)

    axes.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    axes.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

    # Plot Graph tile and axis labels.
    # plt.title("ReBBR: Comparing CUBIC and BBR performance on lossy links")
    plt.ylabel("Goodput (Mbps)", size=20)
    plt.xlabel("Loss Rate (%) - Log Scale", size=20)

    # Plot Graph legend
    plt.legend(loc='upper right', fontsize=20)
    plt.tight_layout()

    # Save the figure first.
    # TODO(jmuindi): Make the figure parameter configurable.
    plt.savefig("figure8.png")
    # Then show the figure interactively
    plt.show()


def main():
    """Run the experiments."""
    debug_print("Replicating Google BBR Figure 8.")
    logfile = './experiment_log.csv'
    with open(logfile, "w") as log:
        log.write("cc, loss, goodput\n")

    # Grab the experimental parameters
    _parse_args()

    # Generate the trace files based on the parameter
    _generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.up")
    _generate_100mpbs_trace(Flags.parsed_args[Flags.TIME], "100Mbps.down")

    port = Flags.parsed_args[Flags.PORT]
    loss = Flags.parsed_args[Flags.LOSS]
    cc = Flags.parsed_args[Flags.CC]
    for cong_ctrl in ['bbr', cc]:
        # Start the server
        server_proc = _start_server(port, loss, cong_ctrl)
        client_proc = _run_experiment(loss, port, cong_ctrl)

        while True:
            client_proc.poll()
            if client_proc.returncode is not None:
                time.sleep(1.5)  # Give the server time to log the results.
                server_proc.terminate()
                break

    debug_print("Experiment complete! Data stored in: " + str(logfile))
    debug_print("Terminating driver.")

    # TODO(luke) Make the graphs from that CSV
    # _make_plots(logfile)


if __name__ == '__main__':
    main()
