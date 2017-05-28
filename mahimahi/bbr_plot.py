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


def get_loss_percent_xmark_ticks(results):
    """Returns a list of x mark ticks for loss rate.

    Results: this is a python dictionary of parsed bbr experiment results. """
    output = []
    for cc, value in results.iteritems():
        for loss in value['loss']:
            output.append(loss)
    return output


def is_same_float(a, b, tolerance=1e-09):
    """ Returns true if the two floats numbers (a,b) are almost equal."""
    abs_diff = abs(a-b)
    return abs_diff < tolerance

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

def parse_results_csv(input_csv_file, include_predicate_fn=None):
    """ Reads input csv file from bbr experiment and converts it into a python dictionary
       convenient for plotting figures.

    input_csv_file: Input CSV file to read.
    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, bandwidth]

    include_predicate_fn: Optional. When present, it's a function called to determine
    whether current record should be included. Function is given a tuple of
    (congestion_control, loss, goodput, rtt, bandwidth) and should return a boolean. True
    for inclusion; False for exclusion.

    Returns a result which an in-memory dictionary of format:
    CongestionControlAlgorithm -> {"loss": [...], "goodput": [...], "rtt" : [...], "bandwidth": [...] }
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
            bandwidth = float(bandwidth)
            if not cc:
                debug_print_warn("Skipping a log entry that's missing a Congestion Control Algorithm")
                continue

            # Skip rows that are filt
            if include_predicate_fn:
                if not include_predicate_fn(cc, loss, goodput, rtt, bandwidth):
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

    # For available options on plot() method, see: https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot
    # We prefer to use explicit keyword syntax to help code readability.

    # Create a figure.
    fig_width = 8
    fig_height = 5
    fig, axes = plt.subplots(figsize=(fig_width, fig_height))

    results = parse_results_csv(logfile)
    xmark_ticks = get_loss_percent_xmark_ticks(results)
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


def make_experiment1_figure(logfile):
    """Generate high quality plot of data for Experiment 1.

    Experiment 1 is looking at effects of various bandwithd between CUBIC and
    BBR.

    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, bandwidth]
    """
    results = {}

    # For available options on plot() method, see: https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot
    # We prefer to use explicit keyword syntax to help code readability.

    # Create a figure.
    fig_width = 8
    fig_height = 5
    fig, axes = plt.subplots(figsize=(fig_width, fig_height))

    results = parse_results_csv(logfile)
    xmark_ticks = get_loss_percent_xmark_ticks(results)
    cubic = results['cubic']
    bbr = results['bbr']
    debug_print_verbose("--- Generating figures for experiment 1")


    bandwidth_filter_list = set(cubic['bandwidth'])
    
    debug_print_verbose("Bandwidth list: %s" % bandwidth_list)


    matplotlib.rcParams.update({'figure.autolayout': True})
    plt.xscale('log')
    deduplicate_xmark_ticks(xmark_ticks)
    apply_axes_formatting(axes, xmark_ticks)

    # See: https://matplotlib.org/examples/color/named_colors.html for available colors.
    # Need 5 colors  since we look at bandwidths: [0.01, 0.1, 1.0,  10.03, 100.27 ]
    cubic_bandwidth_colors = ['blue', 'purple', 'green', 'yellow', 'pink']
    bbr_bandwidth_colors = ['red',    'brown', 'crimson', 'darkcyan', 'olive']
    for index, bandwidth_filter in enumerate(bandwidth_filter_list):
        def include_predicate_fn(congestion_control, loss, goodput, rtt, bandwidth):
            return is_same_float(bandwidth, bandwidth_filter)

        filtered_result = parse_results_csv(logfile, include_predicate_fn)
        filtered_cubic = filtered_result['cubic']
        filtered_bbr = filtered_result['bbr']
        debug_print_verbose("Filtered Results : %s" % filtered_result)
        debug_print_verbose("Filter CUBIC: %s" % filtered_cubic)
        debug_print_verbose("Filter BBR: %s" % filtered_bbr)

        cubic_color = cubic_bandwidth_colors[index]
        bbr_color = bbr_bandwidth_colors[index]

        plt.plot(filtered_cubic['loss'], filtered_cubic['goodput'],
                 color=cubic_color, linestyle='solid', marker='o',
                 markersize=7, label='CUBIC (%s Mbps)' % bandwidth_filter)

        plt.plot(filtered_bbr['loss'], filtered_bbr['goodput'], color=bbr_color,
                 linestyle='solid', marker='x',
                 markersize=7, label='BBR (%s Mbps)' % bandwidth_filter)

    plot_titles(plt,
                xaxis="Loss Rate (%) - Log Scale",
                yaxis="Goodput (Mbps)",
                title="Comparisons CUBIC and BBR performance across various loss rates and bandwidths")

    plot_legend(plt)

    save_figure(plt, name="experiment1_figure.png")


def main():
    debug_print_verbose('Generating Plots')
    #make_figure_8_plot('data/figure8_experiment.csv')
    make_experiment1_figure('data/experiment1.csv')
    #make_experiment2_figure('data/experiment2.csv')
    #make_experiment3_figure('data/expeirment3.csv')

    # TODO(jmuindi): Add plot for experiment 4 (testing against verizon cellular link)
    # when we have data collection for it.
                          

if __name__ == '__main__':
    main()
