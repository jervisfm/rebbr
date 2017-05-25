#!/usr/bin/python
"""Client that sends to server."""

from bbr_logging import debug_print, debug_print_error, debug_print_verbose
import os
import random
import socket
import string
import sys


TCP_CONGESTION = 13


def run_client(cong_control, size=1024, address=(os.environ.get("MAHIMAHI_BASE") or "127.0.0.1"), port=5050):
    """Run the client."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, cong_control)
    debug_print(address)
    try:
        s.connect((address, port))
        debug_print_verbose("connection established")
    except socket.error as msg:
        debug_print_error("cannot connect: " + str(msg))
        sys.exit(-1)

    # Generate a random message of SIZE a single time. Send this over and over.
    msg = ''.join(random.choice(string.ascii_letters) for _ in range(size))

    while True:
        s.send(msg)
