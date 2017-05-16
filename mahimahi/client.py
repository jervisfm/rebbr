#!/usr/bin/python
"""Client that can be CUBIC or BBR."""

import argparse
from bbr_logging import debug_print, debug_print_error, debug_print_verbose
import os
import random
import socket
import string
import sys


TCP_CONGESTION = 13


class Flags(object):
    """Dictionary object to store parsed flags."""

    PORT = "port"
    CC = "congestion_control"
    ADDR = "address"
    SIZE = "packet_size"
    parsed_args = None


def _check_cc(input):
    if input == "bbr" or input == "BBR":
        return "bbr"
    elif input == "cubic" or input == "CUBIC":
        return "cubic"
    else:
        raise argparse.ArgumentTypeError("Choose 'bbr' or 'cubic' as CC.")


def parse_args():
    """Parse experimental parameters from the commandline."""
    parser = argparse.ArgumentParser(
        description="Process experimental params.")
    parser.add_argument('PORT', dest=Flags.PORT, type=int,
                        help="Enter the port number to connect to.",
                        default=5050)
    parser.add_argument('CC', dest=Flags.CC, type=_check_cc,
                        help="Congestion control algorithm to use.",
                        default="cubic")
    parser.add_argument('--addr', dest=Flags.ADDR, type=_check_cc,
                        help="Address to connect to.",
                        default=(os.environ.get("MAHIMAHI_BASE") or "127.0.0.1"))
    parser.add_argument('--size', dest=Flags.SIZE, type=int,
                        help="Size of messages to send.",
                        default=1024)

    Flags.parsed_args = vars(parser.parse_args())
    debug_print_verbose("Parse: " + str(Flags.parsed_args))


def run_client():
    """Run the client."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cong_control = Flags.parsed_args[Flags.CC]
    size = Flags.parsed_args[Flags.SIZE]
    address = Flags.parsed_args[Flags.ADDR]
    port = Flags.parsed_args[Flags.PORT]

    s.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, cong_control)
    debug_print(address)
    try:
        s.connect((address, port))
        debug_print("connection established")
    except socket.error as msg:
        debug_print_error("cannot connect: " + msg)
        sys.exit(-1)

    # Generate a random message of SIZE a single time. Send this over and over.
    msg = ''.join(random.choice(string.ascii_letters) for _ in range(size))

    while True:
        s.send(msg)

if __name__ == '__main__':
    run_client()
