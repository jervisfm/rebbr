#!/usr/bin/python

"""
Test code for making the figure plots
"""
import bbr_plot
from bbr_logging import debug_print, debug_print_verbose, debug_print_error


def run_test_plot():
    logfile = "./test_experiment_log.csv"
    debug_print("Running graph generation for %s" % logfile)
    bbr_plot.make_figure_8_plot(logfile)


def main():
    run_test_plot()

if __name__ == '__main__':
    main()
