#!/usr/bin/python
"""Simple Python Server."""
from bbr_logging import debug_print, debug_print_error, debug_print_verbose
import select
import socket
import sys
import time


def _handle_connection(q, e, conn, size, cc):
    num_msg = 0
    start_time = time.time()
    conn.setblocking(0)  # set to non-blocking
    timeout_in_seconds = 1.0
    last_log_time_secs = time.time()
    log_interval_secs = 5
    while not e.is_set():
        time_now_secs = time.time()
        delta_secs = time_now_secs - last_log_time_secs
        if (delta_secs > log_interval_secs):
            debug_print_verbose("Server Heartbeat. e.is_set()" % e.is_set())
            last_log_time_secs = time_now_secs
        ready = select.select([conn], [], [], timeout_in_seconds)
        if ready[0]:
            # Only read the data if there is data to receive.
            conn.recv(size)
        num_msg += 1

    # Once the event is set, break out
    elapsed_time = time.time() - start_time
    debug_print_verbose("Num msg: " + str(num_msg))
    debug_print_verbose("Size: " + str(size) + " bytes")
    debug_print_verbose("Time: " + str(elapsed_time))
    goodput = (num_msg * size * 8) / elapsed_time / 1e6

    # Send the Goodput back to the master
    q.put(str(goodput))


def run_server(q, e, cc, port=5050, size=1024):
    """Run the server continuously."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(('', port))
    except socket.error:
        debug_print_error("bind error")
        sys.exit(-1)

    s.listen(1)  # only have 1 connection
    debug_print("Server Awaiting connection on port %d" % port)

    conn, _ = s.accept()
    debug_print("Server Accepted connection")
    _handle_connection(q, e, conn, size, cc)
    s.shutdown()
    s.close()
    debug_print("Shutdown server")
