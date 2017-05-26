from __future__ import print_function

import sys

DEBUG_LOG_ENABLED = False

# Debug Levels
DEBUG_LOG_ERROR = 0
DEBUG_LOG_WARN = 1
DEBUG_LOG_INFO = 2
DEBUG_LOG_VERBOSE = 3

# Only output messages upto the Info Level by default.
DEBUG_LOG_LEVEL = DEBUG_LOG_VERBOSE


def debug_print(msg):
    """Print a info debug message."""
    return debug_print_info(msg)


def debug_print_level(level, msg):
    """Log a debug message and print it out to standard output stream.

    All logging should happen via this function or it's related neighbors so that it can easily be controlled
    (e.g. disabled for submission).
    level: One of DEBUG_LOG_{ERROR, WARN, INFO, VERBOSE} indicate level of the message to be logged
    msg: message to log.
    """
    if level < 0:
        return

    should_log = (level <= DEBUG_LOG_LEVEL and DEBUG_LOG_ENABLED)
    if not should_log:
        return
    # Color the log level prefixes. See
    # https://en.wikipedia.org/wiki/ANSI_escape_code#Colors for ANSI color
    # codes.
    if level == DEBUG_LOG_ERROR:
        # Red color
        print("\x1b[31m", end='')
        print("[ERROR] ", end='')
        print("\x1b[0m", end='')
    elif level == DEBUG_LOG_WARN:
        # Yellow color
        print("\x1b[33m", end='')
        print("[WARNING] ", end='')
        print("\x1b[0m", end='')
    elif level == DEBUG_LOG_INFO:
        # Green color
        print("\x1b[32m", end='')
        print("[INFO] ", end='')
        print("\x1b[0m", end='')
    elif level == DEBUG_LOG_VERBOSE:
        # Blue color
        print("\x1b[34m", end='')
        print("[VERBOSE] ", end='')
        print("\x1b[0m", end='')
    # Finally log the message
    print(msg)


def debug_print_info(msg):
    """Print info debug message."""
    return debug_print_level(DEBUG_LOG_INFO, msg)


def debug_print_error(msg):
    """Print error debug message."""
    return debug_print_level(DEBUG_LOG_ERROR, msg)


def debug_print_warn(msg):
    """Print warning debug message."""
    return debug_print_level(DEBUG_LOG_WARN, msg)


def debug_print_verbose(msg):
    """Print verbose debug message."""
    return debug_print_level(DEBUG_LOG_VERBOSE, msg)


def stderr_print(msg):
    """Print a msg to stderr."""
    print(msg, file=sys.stderr)


def stdout_print(msg):
    """Print msg as is without any extra new lines."""
    print(msg, file=sys.stdout, end='')
