#!/usr/bin/python
"""Client that sends to server."""

from bbr_logging import debug_print, debug_print_error, debug_print_verbose
import os
import random
import socket
import string
import sys
import time


TCP_CONGESTION = 13


def run_client(cong_control, size=1024, address=(os.environ.get("MAHIMAHI_BASE") or "127.0.0.1"), port=5050):
    """Run the client."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, cong_control)
    debug_print("Client Connecting to: " + str(address) + ":" + str(port))
    try:
        s.connect((address, port))
        debug_print_verbose("Connection Established")
    except socket.error as msg:
        debug_print_error("Cannot Connect: " + str(msg))
        sys.exit(-1)

    # Generate a random message of SIZE a single time. Send this over and over.
    msg = ''.join(random.choice(string.ascii_letters) for _ in range(size))

    msg_count = 1
    # It can take different amount of time  to send message depending on network
    # configurations. Thus, log progress based on time intervals.
    # TODO(jmuindi): Nice to have - plumb through remaining time of trace ...
    last_log_time_secs = time.time()
    log_interval_secs = 5
    debug_print_verbose("Client Starting Sending Messages...")
    while True:
        time_now_secs = time.time()
        delta_secs = time_now_secs - last_log_time_secs
        if (delta_secs > log_interval_secs):
            debug_print_verbose("Sending Message #%d" % msg_count)
            last_log_time_secs = time_now_secs
        s.send(msg)
        msg_count += 1
