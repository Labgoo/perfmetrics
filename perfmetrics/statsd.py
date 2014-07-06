import logging
import random
import socket
import time
from logging.handlers import DatagramHandler
import re


class StatsdClient(object):
    """Send packets to statsd.

    Derived from statsd.py by Steve Ivy <steveivy@gmail.com>.
    """

    def __init__(self, host='localhost', port=8125, prefix=''):
        # Resolve the host name early.
        info = socket.getaddrinfo(host, int(port), 0, socket.SOCK_DGRAM)
        family, socktype, proto, _canonname, addr = info[0]
        self.addr = addr
        self.log = logging.getLogger(__name__)
        self.inactivity = time.clock()
        self.socket_handler = DatagramHandler(host, port)
        self.random = random.random  # Testing hook
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

    def _send(self, data):
        """Send a UDP packet containing a string."""
        try:
            self.socket_handler.send(self._encode(data))
        except socket.error, msg:
            message = str(msg[0]).strip()
            match = re.search('broken', str(msg[1]))
            self.log.warning('Failed to send UDP packet, Error Code : %s Message : %s', message, str(msg[1]))
            if message == '31' or message == '32' or match:
                self.socket_handler.sock = None
                self.log.warning('Restarting socket')

    def sendbuf(self, buf):
        """Send a UDP packet containing string lines."""
        try:
            if buf:
                self.socket_handler.send(self._encode('\n'.join(buf)))
        except socket.error, msg:
            code = str(msg[0]).strip()
            match = re.search('broken', str(msg[1]))
            self.log.warning('Failed to send UDP packet, Error Code : %s Message : %s', code, str(msg[1]))
            if code == '31' or code == '32' or match:
                self.socket_handler.sock = None
                self.log.warning('Restarting socket')

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
