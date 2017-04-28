# -*- coding: utf-8 -*-
mport logging
import urlparse
from time import time
from os import getpid
from re import match, compile
from struct import unpack
from socket import gethostbyname, gethostname, inet_aton
from itertools import cycle

class TraceIdGenerator(object):

    pid = getpid()
    ip = gethostbyname(gethostname())
    cycle_counter = cycle(xrange(1000, 9000))
    ip_hex = IP_HEX
    pid_hex = PID
    try:
        ip_hex = get_hex_ip(ip)
        pid_hex = get_hex_pid(pid)
    except Exception, ex:
        SysLogger.exception(ex)

    @staticmethod
    def get_traceid():
        return "%s%d%d%s%s" % (TraceIdGenerator.ip_hex, int(time()*1000), TraceIdGenerator.cycle_counter.next(),
                               PID_FLAG, TraceIdGenerator.pid_hex)