# -*- coding: utf-8 -*-
from time import time
from os import getpid
from re import match, compile
from struct import unpack
from socket import gethostbyname, gethostname, inet_aton
from itertools import cycle


class TraceIdGenerator(object):
    IP_HEX = "ffffffff"
    IP_INIT = "255255255255"
    PID_FLAG = "d"
    REGEX = "\\b((?!\\d\\d\\d)\\d+|1\\d\\d|2[0-4]\\d|25[0-5])\\.((?!\\d\\d\\d)\\d+|1\\d\\d|2[0-4]\\d|25[0-5])\\." \
            "((?!\\d\\d\\d)\\d+|1\\d\\d|2[0-4]\\d|25[0-5])\\.((?!\\d\\d\\d)\\d+|1\\d\\d|2[0-4]\\d|25[0-5])\\b"
    PATTERN = compile(REGEX)
    PID = "0000"

    pid = getpid()
    ip = gethostbyname(gethostname())
    cycle_counter = cycle(xrange(1000, 9000))
    ip_hex = IP_HEX
    pid_hex = PID

    @classmethod
    def get_hex_ip(cls, ip):
        if ip:
            ip_hex = '%08x' % unpack("!I", inet_aton(ip))[0]  # 将ip地址转换为16进制字符串
        else:
            ip_hex = cls.IP_HEX
        return ip_hex

    @classmethod
    def get_hex_pid(cls, pid):
        if pid < 0:
            pid = 0
        elif pid > 65536:
            pid = pid % 65536
        pid_str = '%04x' % pid  # pid 转化为4位16进制字符
        return pid_str

    @classmethod
    def get_trace_id(cls):
        ip_hex = cls.get_hex_ip(cls.ip)
        pid_hex = cls.get_hex_pid(cls.pid)
        trace_id = '{ip}{ts}{count}{flag}{pid}'.format(
            ip=ip_hex,
            ts=int(time() * 1000),
            count=cls.cycle_counter.next(),
            flag=cls.PID_FLAG,
            pid=pid_hex
        )
        return trace_id
