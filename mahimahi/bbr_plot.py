#!/usr/bin/python
"""Module for creating all of the plots after the data has been gathered."""
from bbr_logging import debug_print, debug_print_verbose, debug_print_error, debug_print_warn
import csv
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import os

# Flag to control whether interactive plots should be shown.
SHOW_INTERACTIVE_PLOTS = False


def deduplicate_xmark_ticks(xmark_ticks):
    """Remove redundant ticks for the given xmark_ticks."""
    # Use a set to deduplicate.
    xmark_ticks = sorted([x for x in set(xmark_ticks)])
    xmark_ticks.remove(25.0)
    xmark_ticks.remove(15.0)
    xmark_ticks.remove(40.0)
    return xmark_ticks


def get_loss_percent_xmark_ticks(results):
    """Return a list of x mark ticks for loss rate.

    Results: this is a python dictionary of parsed bbr experiment results.
    """
    output = []
    for cc, value in results.iteritems():
        for loss in value['loss']:
            output.append(loss)
    return output


def is_same_float(a, b, tolerance=1e-09):
    """Return true if the two floats numbers (a,b) are almost equal."""
    abs_diff = abs(a - b)
    return abs_diff < tolerance


def apply_axes_formatting(axes, xmark_ticks):
    """Format axes."""
    # For each loss percent, set a mark on x-axis.
    axes.set_xticks(xmark_ticks)

    # Make the X-Axis label look vertical to make them more readable.
    axes.set_xticklabels(axes.xaxis.get_majorticklabels(),
                         rotation=90, fontsize=14)

    # Format the Y-Axis too
    axes.set_yticklabels(axes.yaxis.get_majorticklabels(), fontsize=14)

    axes.get_xaxis().set_major_formatter(matplotlib.ticker.FormatStrFormatter('%g'))
    axes.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())


def plot_legend(plt, axes, ncol=2, fontsize=20):
    """Plot legend."""
    # Sort the labels
    handles, labels = axes.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))

    # Plot Graph legend
    plt.legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .102), ncol=ncol,
               mode="expand", loc=3, fontsize=fontsize, borderaxespad=0.)
    plt.tight_layout()


def plot_titles(plt, xaxis=None, yaxis=None, title=None):
    """Plot graph titles."""
    # Plot Graph tile and axis labels as appropriate.
    if title:
        plt.title(title)
    if xaxis:
        plt.xlabel(xaxis, size=20)
    if yaxis:
        plt.ylabel(yaxis, size=20)


def save_figure(plt, name):
    """Save the graphic and maybe shows it interactively."""
    # Save the figure first.
    plt.savefig(name, bbox_inches='tight')
    # May be show the figure interactively
    if SHOW_INTERACTIVE_PLOTS:
        plt.show()


def parse_results_csv(input_csv_file, include_predicate_fn=None):
    """Read input csv file from bbr experiment and converts it into a python dictionary convenient for plotting figures.

    input_csv_file: Input CSV file to read.
    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, capacity, specified_bw]

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

        for (cc, loss, goodput, rtt, capacity, specified_bw) in reader:
            loss_percent = float(loss) * 100
            goodput = float(goodput)
            rtt = float(rtt)
            capacity = float(capacity)
            specified_bw = float(specified_bw)
            normalized_goodput = goodput / capacity
            if not cc:
                debug_print_warn(
                    "Skipping a log entry that's missing a Congestion Control Algorithm")
                continue

            # Skip rows that are filt
            if include_predicate_fn:
                if not include_predicate_fn(cc, loss, goodput, rtt, capacity, specified_bw):
                    continue

            if cc in results:
                # Re-use existing dictionary
                value_dict = results[cc]
            else:
                # Create a new one.
                value_dict = {"loss": [], "goodput": [],
                              "normalized_goodput": [], "rtt": [], "capacity": [], "specified_bw": []}

            value_dict['loss'].append(loss_percent)
            value_dict['goodput'].append(goodput)
            value_dict['rtt'].append(rtt)
            value_dict['capacity'].append(capacity)
            value_dict['specified_bw'].append(specified_bw)
            value_dict['normalized_goodput'].append(normalized_goodput)
            results[cc] = value_dict
    return results


def make_figure_8_plot(logfile):
    """Generate high quality plot of data to reproduce figure 8.

    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, capacity, specified_bw]
    """
    results = {}
    plt.figure()
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

    # Plot ideal line of (1-lossRate * BW)
    ideal = {}
    ideal['loss'] = cubic['loss']
    ideal['goodput'] = [(1 - (x / 100.0)) * 100 for x in ideal['loss']]

    plt.plot(ideal['loss'], ideal['goodput'], color='black', linestyle='dotted', label='ideal')

    plt.xscale('log')

    plot_titles(plt, xaxis="Loss Rate (%) - Log Scale", yaxis="Goodput (Mbps)")

    apply_axes_formatting(axes, deduplicate_xmark_ticks(xmark_ticks))
    plot_legend(plt, axes, ncol=3)

    save_figure(plt, name="figures/figure8.png")


def make_experiment1_figure(logfile):
    """Generate high quality plot of data for Experiment 1.

    Experiment 1 is looking at effects of various bandwithd between CUBIC and
    BBR.

    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, capacity, specified_bw]
    """
    results = {}
    plt.figure()
    # For available options on plot() method, see: https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot
    # We prefer to use explicit keyword syntax to help code readability.

    # Create a figure.
    fig_width = 8
    fig_height = 5
    fig, axes = plt.subplots(figsize=(fig_width, fig_height))

    results = parse_results_csv(logfile)
    debug_print_verbose('Parsed Results: %s' % results)
    xmark_ticks = get_loss_percent_xmark_ticks(results)
    cubic = results['cubic']
    debug_print_verbose("--- Generating figures for experiment 1")

    bandwidth_filter_list = sorted(list(set(cubic['specified_bw'])))

    debug_print_verbose("Bandwidth list: %s" % bandwidth_filter_list)

    matplotlib.rcParams.update({'figure.autolayout': True})
    plt.xscale('log')

    #  Tool for easily visualing color schemes:
    #  http://colorbrewer2.org/#type=sequential&scheme=Reds&n=8
    cubic_bandwidth_colors = ['#9ecae1',
                              '#6baed6', '#4292c6', '#2171b5', '#084594']
    bbr_bandwidth_colors = ['#fc9272', '#fb6a4a',
                            '#ef3b2c', '#cb181d', '#99000d']

    for index, bandwidth_filter in enumerate(bandwidth_filter_list):
        def include_predicate_fn(congestion_control, loss, goodput, rtt, capacity, specified_bw):
            return is_same_float(specified_bw, bandwidth_filter)

        filtered_result = parse_results_csv(logfile, include_predicate_fn)
        debug_print_verbose("Filtered Results %s : %s" %
                            (bandwidth_filter, filtered_result))
        filtered_cubic = filtered_result['cubic']
        filtered_bbr = filtered_result['bbr']
        debug_print_verbose("Filter CUBIC: %s" % filtered_cubic)
        debug_print_verbose("Filter BBR: %s" % filtered_bbr)

        cubic_color = cubic_bandwidth_colors[index]
        bbr_color = bbr_bandwidth_colors[index]

        plt.plot(filtered_cubic['loss'], filtered_cubic['normalized_goodput'],
                 color=cubic_color, linestyle='solid', marker='o',
                 markersize=7, label='CUBIC (%s Mbps)' % bandwidth_filter)

        plt.plot(filtered_bbr['loss'], filtered_bbr['normalized_goodput'], color=bbr_color,
                 linestyle='solid', marker='x',
                 markersize=7, label='BBR (%s Mbps)' % bandwidth_filter)

    plot_titles(plt,
                xaxis="Loss Rate (%) - Log Scale",
                yaxis="Normalized Goodput")

    apply_axes_formatting(axes, deduplicate_xmark_ticks(xmark_ticks))
    plot_legend(plt, axes, fontsize=10)

    save_figure(plt, name="figures/experiment1.png")


def make_experiment2_figure(logfile):
    """Generate high quality plot of data to reproduce figure for experiment 2.

    Looking at performance of different congestion control algorithms.
    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, capacity, specified_bw]
    """
    results = {}
    plt.figure()
    # For available options on plot() method, see: https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot
    # We prefer to use explicit keyword syntax to help code readability.

    # Create a figure.
    fig_width = 8
    fig_height = 5
    fig, axes = plt.subplots(figsize=(fig_width, fig_height))

    results = parse_results_csv(logfile)
    xmark_ticks = get_loss_percent_xmark_ticks(results)
    # We gather results for the following congestion control algoirhtms:
    # cubic bbr bic vegas westwood reno
    cubic = results['cubic']
    bbr = results['bbr']

    bic = results['bic']
    vegas = results['vegas']
    westwood = results['westwood']
    reno = results['reno']

    debug_print_verbose("CUBIC: %s" % cubic)
    debug_print_verbose("BBR: %s" % bbr)
    debug_print_verbose("BIC: %s" % bic)
    debug_print_verbose("VEGAS: %s" % vegas)
    debug_print_verbose("WESTWOOD: %s" % westwood)
    debug_print_verbose("RENO: %s" % reno)

    matplotlib.rcParams.update({'figure.autolayout': True})

    # Plot the results of the different congestion control algorithms
    plt.plot(cubic['loss'], cubic['goodput'], color='blue', linestyle='solid', marker='o',
             markersize=7, label='CUBIC')

    plt.plot(bbr['loss'], bbr['goodput'], color='red', linestyle='solid', marker='x',
             markersize=7, label='BBR')

    plt.plot(bic['loss'], bic['goodput'], color='#addd8e', linestyle='solid', marker='.',
             markersize=7, label='BIC')

    plt.plot(vegas['loss'], vegas['goodput'], color='#78c679', linestyle='solid', marker='.',
             markersize=7, label='VEGAS')

    plt.plot(westwood['loss'], westwood['goodput'], color='#31a354', linestyle='solid', marker='.',
             markersize=7, label='WESTWOOD')

    plt.plot(reno['loss'], reno['goodput'], color='#006837', linestyle='solid', marker='.',
             markersize=7, label='RENO')

    plt.xscale('log')

    plot_titles(plt, xaxis="Loss Rate (%) - Log Scale",
                yaxis="Goodput (Mbps)")

    apply_axes_formatting(axes, deduplicate_xmark_ticks(xmark_ticks))
    plot_legend(plt, axes, ncol=3, fontsize=10)

    save_figure(plt, name="figures/experiment2.png")


def make_experiment3_figure(logfile):
    """Generate high quality plot of data for Experiment 3.

    Experiment 3 is looking at effects of various RTTs values  between CUBIC and
    BBR.

    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, capacity, specified_bw]
    """
    results = {}
    plt.figure()
    # For available options on plot() method, see: https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot
    # We prefer to use explicit keyword syntax to help code readability.

    # TODO(jmuindi): Check that this graph generation works.

    # Create a figure.
    fig_width = 8
    fig_height = 5
    fig, axes = plt.subplots(figsize=(fig_width, fig_height))

    results = parse_results_csv(logfile)
    xmark_ticks = get_loss_percent_xmark_ticks(results)
    cubic = results['cubic']
    debug_print_verbose("--- Generating figures for experiment 3")

    rtt_filter_list = sorted(list(set(cubic['rtt'])))

    debug_print_verbose("RTT list: %s" % rtt_filter_list)

    matplotlib.rcParams.update({'figure.autolayout': True})

    # See: https://matplotlib.org/examples/color/named_colors.html for available colors.
    # Need 5 colors  since we look at 5 RTT values (ms): [2 10 100 1000 10000]
    cubic_rtt_colors = ['#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#084594']
    bbr_rtt_colors = ['#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#99000d']
    for index, rtt_filter in enumerate(rtt_filter_list):
        def include_predicate_fn(congestion_control, loss, goodput, rtt, capacity, specified_bw):
            return is_same_float(rtt, rtt_filter)

        filtered_result = parse_results_csv(logfile, include_predicate_fn)
        filtered_cubic = filtered_result['cubic']
        filtered_bbr = filtered_result['bbr']
        debug_print_verbose("Filtered Results : %s" % filtered_result)
        debug_print_verbose("Filter CUBIC: %s" % filtered_cubic)
        debug_print_verbose("Filter BBR: %s" % filtered_bbr)

        cubic_color = cubic_rtt_colors[index]
        bbr_color = bbr_rtt_colors[index]

        plt.plot(filtered_cubic['loss'], filtered_cubic['goodput'],
                 color=cubic_color, linestyle='solid', marker='o',
                 markersize=7, label='CUBIC (%s ms RTT)' % rtt_filter)

        plt.plot(filtered_bbr['loss'], filtered_bbr['goodput'], color=bbr_color,
                 linestyle='solid', marker='x',
                 markersize=7, label='BBR (%s ms RTT)' % rtt_filter)

    plot_titles(plt,
                xaxis="Loss Rate (%) - Log Scale",
                yaxis="Goodput (Mbps)")

    plt.xscale('log')
    apply_axes_formatting(axes, deduplicate_xmark_ticks(xmark_ticks))

    # Sort the labels.
    # NOTE: Not using the helper function because we need to specifically
    # handle the fact that the strings aren't in perfect alphabetical order.
    handles, labels = axes.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles),
                                  key=lambda t: t[0].split(' ', 1)[0]))

    # Plot Graph legend
    plt.legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .102), ncol=2,
               mode="expand", loc=3, fontsize=10, borderaxespad=0.)
    plt.tight_layout()

    save_figure(plt, name="figures/experiment3.png")


def make_experiment4_figure(logfile):
    """Generate high quality plot of data to reproduce figure 8.

    The logfile is a CSV of the format [congestion_control, loss_rate, goodput, rtt, capacity, specified_bw]
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

    apply_axes_formatting(axes, deduplicate_xmark_ticks(xmark_ticks))

    plot_titles(plt, xaxis="Loss Rate (%) - Log Scale", yaxis="Goodput (Mbps)")

    plot_legend(plt, axes)

    save_figure(plt, name="figures/experiment4.png")


def main():
    """Plot all figures."""
    debug_print_verbose('Generating Plots')

    if not os.path.exists('figures'):
        os.makedirs('figures')

    make_figure_8_plot('data/figure8.csv')
    make_experiment1_figure('data/experiment1.csv')
    make_experiment2_figure('data/experiment2.csv')
    make_experiment3_figure('data/experiment3.csv')
    make_experiment4_figure('data/experiment4.csv')


if __name__ == '__main__':
    main()
