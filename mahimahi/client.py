#!/usr/bin/python
"""Client that sends to server."""

from bbr_logging import debug_print, debug_print_error, debug_print_verbose
import os
import random
import socket
import string
import time


def run_client(cong_control, size=1024, address=(os.environ.get("MAHIMAHI_BASE") or "127.0.0.1"), port=5050):
    """Run the client."""
    TCP_CONGESTION = 13
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, cong_control)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 6553600)
    debug_print("Client Connecting to: " + str(address) + ":" + str(port))
    try:
        s.connect((address, port))
    except socket.error as msg:
        debug_print_error("Cannot Connect: " + str(msg))
        return

    debug_print("Connection Established.")
    # Generate a random message of SIZE a single time. Send this over and over.
    msg = ''.join(random.choice(string.ascii_lowercase) for _ in range(size))

    debug_print_verbose(msg)

    msg_count = 1
    # It can take different amount of time  to send message depending on network
    # configurations. Thus, log progress based on time intervals.
    last_log_time_secs = time.time()
    log_interval_secs = 5
    debug_print("Client Starting Sending Messages...")
    while True:
        time_now_secs = time.time()
        delta_secs = time_now_secs - last_log_time_secs
        if (delta_secs > log_interval_secs):
            debug_print("Sending Message #%d" % msg_count)
            last_log_time_secs = time_now_secs
        try:
            s.send(msg)
        except Exception as e:
            debug_print_error("Socket Send Exception: " + str(e))
            return
        msg_count += 1
