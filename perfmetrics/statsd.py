import logging
import random
import socket
import time
from logging.handlers import DatagramHandler
import re
import errno


class StatsdClient(object):
    """Send packets to statsd.

    Derived from statsd.py by Steve Ivy <steveivy@gmail.com>.
    """

    def __init__(self, host='localhost', port=8125, prefix='', unique=False):
        # Resolve the host name early.
        info = socket.getaddrinfo(host, int(port), 0, socket.SOCK_DGRAM)
        family, socktype, proto, _canonname, addr = info[0]
        self.addr = addr
        self.log = logging.getLogger(__name__)
        self.inactivity = time.clock()
        self.socket_handler = DatagramHandler(host, port)
        self.random = random.random  # Testing hook
        self.unique = unique
        if prefix and not prefix.endswith('.'):
            prefix = prefix + '.'
        self.prefix = prefix

    def timing(self, stat, value, rate=1, buf=None, rate_applied=False):
        """Log timing information in milliseconds.

        >>> client = StatsdClient()
        >>> client.timing('some.time', 500)
        """
        if rate >= 1 or rate_applied or self.random() < rate:
            s = '%s%s:%d|ms' % (self.prefix, stat, value)
            if buf is None:
                self._send(s)
            else:
                buf.append(s)

    def gauge(self, stat, value, rate=1, buf=None, rate_applied=False):
        """Log a gauge value.

        >>> client = StatsdClient()
        >>> client.gauge('pool_size', 5)
        """
        if rate >= 1 or rate_applied or self.random() < rate:
            s = '%s%s:%s|g' % (self.prefix, stat, value)
            if buf is None:
                self._send(s)
            else:
                buf.append(s)

    def incr(self, stat, count=1, rate=1, buf=None, rate_applied=False):
        """Increment a counter.

        >>> client = StatsdClient()
        >>> client.incr('some.int')
        >>> client.incr('some.float', 0.5)
        """
        if rate >= 1:
            s = '%s%s:%s|c' % (self.prefix, stat, count)
        elif rate_applied or self.random() < rate:
            s = '%s%s:%s|c|@%s' % (self.prefix, stat, count, rate)
        else:
            return

        if buf is None:
            self._send(s)
        else:
            buf.append(s)

    def decr(self, stat, count=1, rate=1, buf=None, rate_applied=False):
        """Decrement a counter.

        >>> client = StatsdClient()
        >>> client.decr('some.int')
        """
        self.incr(stat, -count, rate=rate, buf=buf, rate_applied=rate_applied)

    def check_exception_and_restart(self, msg, data):
        code, message = msg
        self.log.warning('Failed to send UDP packet, Error Code : %s Message : %s', code, message)
        if code == errno.EPIPE or code == errno.EBADF:
            self.socket_handler.sock = None
            self.log.warning('Restarting socket and resending')
            self.socket_handler.send(data)

    def _send(self, data):
        """Send a UDP packet containing a string."""
        if self.unique:
            import random

            hash = "%x" % (random.getrandbits(128) >> 100)
            data = self._encode(hash + '#' + data)
        try:
            self.socket_handler.send(data)
        except socket.error, exception_message:
            self.check_exception_and_restart(exception_message, data)


    def sendbuf(self, buf):
        """Send a UDP packet containing string lines."""
        data = self._encode('\n'.join(buf))
        try:
            if buf:
                self.socket_handler.send(data)
        except socket.error, exception_message:
            self.check_exception_and_restart(exception_message, data)

    def _encode(self, data):
        return data.encode('ascii', 'replace')


class StatsdClientMod(object):
    """Wrap StatsClient, modifying all stat names in context."""

    def __init__(self, wrapped, format):
        self._wrapped = wrapped
        self.format = format

    def timing(self, stat, *args, **kw):
        self._wrapped.timing(self.format % stat, *args, **kw)

    def gauge(self, stat, *args, **kw):
        self._wrapped.gauge(self.format % stat, *args, **kw)

    def incr(self, stat, *args, **kw):
        self._wrapped.incr(self.format % stat, *args, **kw)

    def decr(self, stat, *args, **kw):
        self._wrapped.decr(self.format % stat, *args, **kw)

    def sendbuf(self, buf):
        self._wrapped.sendbuf(buf)


class NullStatsdClient(object):
    """No-op statsd client."""

    def timing(self, stat, *args, **kw):
        pass

    def gauge(self, stat, *args, **kw):
        pass

    def incr(self, stat, *args, **kw):
        pass

    def decr(self, stat, *args, **kw):
        pass

    def sendbuf(self, buf):
        pass


null_client = NullStatsdClient()
