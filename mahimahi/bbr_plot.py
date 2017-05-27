#!/usr/bin/python
"""Module for creating all of the plots after the data has been gathered."""
from bbr_logging import debug_print, debug_print_verbose, debug_print_error, debug_print_warn
import csv
import matplotlib
from matplotlib import pyplot as plt


# Flag to control whether interactive plots should be shown.
SHOW_INTERACTIVE_PLOTS = False

def deduplicate_xmark_ticks(xmark_ticks):
    """Removes redundant ticks for the given xmark_ticks. """
    # Use a set to deduplicate.
    xmark_ticks = sorted([x for x in set(xmark_ticks)])
    xmark_ticks.remove(25.0)
    xmark_ticks.remove(15.0)
    xmark_ticks.remove(40.0)
    return xmark_ticks


def apply_axes_formatting(axes, xmark_ticks):
    """ Default axes formatting. """
    # For each loss percent, set a mark on x-axis.
    axes.set_xticks(xmark_ticks)

    # Make the X-Axis label look vertical to make them more readable.
    axes.set_xticklabels(axes.xaxis.get_majorticklabels(),
                         rotation=90, fontsize=14)

    # Format the Y-Axis too
    axes.set_yticklabels(axes.yaxis.get_majorticklabels(), fontsize=14)

    axes.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    axes.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())


def plot_legend(plt):
    """ Plots legend. """
    # Plot Graph legend
    plt.legend(loc='upper right', fontsize=20)
    plt.tight_layout()

def plot_titles(plt, xaxis=None, yaxis=None, title=None):
    """Plots graph titles. """

    # Plot Graph tile and axis labels as appropriate.
    if title:
        plt.title(title)
    if xaxis:
        plt.xlabel(xaxis, size=20)
    if yaxis:
        plt.ylabel(yaxis, size=20)


def save_figure(plt, name):
   """ Saves the graphic and maybe shows it interactively. """
   # Save the figure first.
   plt.savefig(name)
   # May be show the figure interactively
   if SHOW_INTERACTIVE_PLOTS:
       plt.show()

def parse_results_csv(input_csv_file):
    """ Reads input csv file from bbr experiment and converts it into a python dictionary
       convenient for plotting figures.

    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, bandwidth]

    """
    # Parse CSV File into in-memory result dictionary. Format is like:
    # CongestionControl -> {"loss": [], "goodput": [], ... }
    results = {}
    with open(input_csv_file, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        # Skip header row
        reader.next()

        for (cc, loss, goodput, rtt, bandwidth) in reader:
            loss_percent = float(loss) * 100
            xmark_ticks.append(loss_percent)

            if not cc:
                debug_print_warn("Skipping a log entry that's missing a Congestion Control Algorithm")
                continue

            if cc in results:
                # Re-use existing dictionary
                value_dict = results[cc]
            else:
                # Create a new one.
                value_dict = { "loss" : [], "goodput": [], "rtt": [], "bandwidth": [] }

            value_dict['loss'].append(loss_percent)
            value_dict['goodput'].append(goodput)
            value_dict['rtt'].append(rtt)
            value_dict['bandwidth'].append(bandwidth)
            results[cc] = value_dict
    return results


def make_figure_8_plot(logfile):
    """Generate high quality plot of data to reproduce figure 8.

    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, bandwidth]
    """
    results = {}
    cubic = {"loss": [], "goodput": []}
    bbr = {"loss": [], "goodput": []}
    xmark_ticks = []

    # For available options on plot() method, see: https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot
    # We prefer to use explicit keyword syntax to help code readability.

    # Create a figure.
    fig_width = 8
    fig_height = 5
    fig, axes = plt.subplots(figsize=(fig_width, fig_height))

    results = parse_results_csv(logfile)
    cubic = results['cubic']
    bbr = results['bbr']
    debug_print_verbose("CUBIC: %s" % cubic)
    debug_print_verbose("BBR: %s" % bbr)

    matplotlib.rcParams.update({'figure.autolayout': True})

    plt.plot(cubic['loss'], cubic['goodput'], color='blue', linestyle='solid', marker='o',
             markersize=7, label='CUBIC')

    plt.plot(bbr['loss'], bbr['goodput'], color='red', linestyle='solid', marker='x',
             markersize=7, label='BBR')

    plt.xscale('log')

    deduplicate_xmark_ticks(xmark_ticks)

    apply_axes_formatting(axes, xmark_ticks)

    plot_titles(plt, xaxis="Loss Rate (%) - Log Scale", yaxis="Goodput (Mbps)")

    plot_legend(plt)

    save_figure(plt, name="figure8.png")



def main():
    debug_print_verbose('Generating Plots')
    make_figure_8_plot('data/figure8_experiment.csv')
    #make_experiment1_plot('data/experiment1.csv')
    #make_experiment2_plot('data/experiment2.csv')
    #make_experiment3_plot('data/expeirment3.csv')

    # TODO(jmuindi): Add plot for experiment 4 (testing against verizon cellular link)
    # when we have data collection for it.
                          

if __name__ == '__main__':
    main()
