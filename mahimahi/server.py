#!/usr/bin/python
"""Simple Python Server."""
from bbr_logging import debug_print, debug_print_error, debug_print_verbose
from multiprocessing import Process
import os
import select
import socket
import sys
import time


class Server(Process):
    """Server class that simply receives data."""

    def __init__(self, outputQueue, event, cc, port=5050, size=1024):
        """Initialize server with input and output Queues."""
        super(Server, self).__init__()
        self.outQ = outputQueue
        self.e = event
        self.cc = cc
        self.port = port
        self.size = size

    def _handle_connection(self, conn):
        num_msg = 0
        start_time = time.time()
        conn.setblocking(0)  # set to non-blocking
        timeout_in_seconds = 1.0
        last_log_time_secs = time.time()
        log_interval_secs = 5
        while not self.e.is_set():
            time_now_secs = time.time()
            delta_secs = time_now_secs - last_log_time_secs
            if (delta_secs > log_interval_secs):
                debug_print_verbose("Server Heartbeat. e.is_set()? %s" % self.e.is_set())
                last_log_time_secs = time_now_secs
            ready = select.select([conn], [], [], timeout_in_seconds)
            if ready[0]:
                # Only read the data if there is data to receive.
                conn.recv(self.size)
            num_msg += 1

        # Once the event is set, break out
        elapsed_time = time.time() - start_time
        debug_print_verbose("Num msg: " + str(num_msg))
        debug_print_verbose("Size: " + str(self.size) + " bytes")
        debug_print_verbose("Time: " + str(elapsed_time))
        goodput = (num_msg * self.size * 8) / elapsed_time / 1e6

        # Send the Goodput back to the master
        self.outQ.put(("Estimated goodput: " + str(goodput), None))

    def run(self):
        """Run the server continuously."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 6553600)
        s.settimeout(120)
        try:
            s.bind(('', self.port))
        except Exception as e:
            debug_print_error("Binding Error: " + str(e))
            self.outQ.put((None, e))
            sys.exit(-1)

        s.listen(1)  # only have 1 connection
        debug_print("Server awaiting connection on port %d" % self.port)

        conn, _ = s.accept()
        debug_print("Server Accepted connection")
        self._handle_connection(conn)
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        debug_print("Shutdown server")
