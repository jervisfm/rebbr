#!/usr/bin/python
"""Simple Python Server."""
import argparse
from bbr_logging import debug_print, debug_print_error, debug_print_verbose
from multiprocessing import Process
import socket
import sys


class Flags(object):
    """Dictionary object to store parsed flags."""

    PORT = "port"
    SIZE = "size"
    parsed_args = None


def parse_args():
    """Parse experimental parameters from the commandline."""
    parser = argparse.ArgumentParser(
        description="Process experimental params.")
    parser.add_argument(Flags.PORT, type=int,
                        help="Enter the port number to connect to.",
                        default=5050)
    parser.add_argument('--size', dest=Flags.SIZE, type=int,
                        help="Size of messages to send.",
                        default=1024)

    Flags.parsed_args = vars(parser.parse_args())
    debug_print_verbose("Parse: " + str(Flags.parsed_args))


def run_server():
    """Run the server continuously."""
    def handle_connection(conn, size):
        num_msg = 0
        while True:
            msg = conn.recv(size)
            if not msg:
                break
            num_msg += 1
        print(num_msg)

    port = Flags.parsed_args[Flags.PORT]
    size = Flags.parsed_args[Flags.SIZE]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind(('', port))
    except socket.error:
        debug_print_error("bind error")
        sys.exit(-1)

    s.listen(1)  # only have 1 connection
    debug_print("Awaiting connection on port %d" % port)

    while (True):
        conn, _ = s.accept()
        debug_print("Accepted connection")
        p = Process(target=handle_connection, args=(conn, size))
        p.start()
        p.join()
    s.close()

if __name__ == '__main__':
    parse_args()
    run_server()
