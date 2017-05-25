#!/usr/bin/python
"""Simple Python Server."""
from bbr_logging import debug_print, debug_print_error, debug_print_verbose
import socket
import sys
import time


def _handle_connection(q, conn, size, cc):
    num_msg = 0
    start_time = time.time()
    while True:
        conn.settimeout(1.0)
        try:
            msg = conn.recv(size)
        except socket.timeout:
            msg = None
        if not msg:
            debug_print_verbose("Closing connection.")
            conn.close()
            break
        num_msg += 1
    elapsed_time = time.time() - start_time
    debug_print_verbose("Num msg: " + str(num_msg))
    debug_print_verbose("Size: " + str(size) + " bytes")
    debug_print_verbose("Time: " + str(elapsed_time))
    goodput = (num_msg * size * 8) / elapsed_time / 1e6
    debug_print("Goodput: " + str(goodput))

    # Send the Goodput back to the master
    q.put(str(goodput))


def run_server(q, cc, port=5050, size=1024):
    """Run the server continuously."""
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
        _handle_connection(q, conn, size, cc)
    s.close()
