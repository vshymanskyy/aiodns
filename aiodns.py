# SPDX-FileCopyrightText: 2024 Volodymyr Shymanskyy
# SPDX-License-Identifier: MIT
#
# The software is provided "as is", without any warranties or guarantees (explicit or implied).
# This includes no assurances about being fit for any specific purpose.

__copyright__ = "2024 Volodymyr Shymanskyy"
__license__ = "MIT"
__version__ = "0.2.0"

import time
import os
import socket
from socket import AF_INET, AF_INET6, SOCK_DGRAM, SOCK_STREAM
from socket import getaddrinfo as _gai
from collections import OrderedDict
from asyncio import sleep_ms

try:
    import network
except ImportError:
    network = None

# import logging
# log = logging.getLogger(__name__)

AF_UNSPEC = 0

servers = {"8.8.8.8", "1.1.1.1", "9.9.9.9"}  # Google, Cloudflare, Quad9
timeout_ms = 5000

cache = OrderedDict()
cache_size = 32
_qtypes = {
    AF_INET: (b"\x00\x01",),  # A
    AF_INET6: (b"\x00\x1c",),  # AAAA
    AF_UNSPEC: (b"\x00\x01", b"\x00\x1c"),
}

def _ip4(s):
    try:
        parts = s.split(".")
        if len(parts) != 4:
            return False
        for p in parts:
            if not 0 <= int(p) <= 255:
                return False
        return True
    except ValueError:
        return False

def _ip6(s):
    try:
        parts = s.split(":")
        if len(parts) > 8 or len(parts) < 3:
            return False
        for p in parts:
            if p and int(p, 16) > 0xFFFF:
                return False
        return True
    except ValueError:
        return False

def _build_dns_query(host, qtype):
    host = host.encode()
    query = bytearray(17 + len(host))  # Header + Hostname + NULL + (Questions * 4)
    query[0:2] = os.urandom(2)  # Transaction ID
    query[2:4] = b"\x01\x00"  # Standard query with recursion desired
    query[4:6] = b"\x00\x01"  # Questions count = 1
    # query[6:12] => Answer RRs, Authority RRs, Additional RRs (all set to 0)
    pos = 12
    for part in host.split(b"."):  # QNAME (hostname in DNS format)
        sz = len(part)
        query[pos] = sz
        pos += 1
        query[pos : pos + sz] = part
        pos += sz
    query[pos] = 0  # Null byte to end QNAME
    pos += 1
    query[pos : pos + 2] = qtype  # QTYPE (A or AAAA)
    query[pos + 2 : pos + 4] = b"\x00\x01"  # QCLASS (IN)
    return query


def _parse_int(b):
    return int.from_bytes(b, "big")


def _parse_dns_rsp(rsp):
    if len(rsp) < 12:
        raise ValueError("Invalid DNS response")

    answer_count = _parse_int(rsp[6:8])
    if not answer_count:
        raise ValueError("Invalid DNS response")

    answers = []
    pos = 12
    for _ in range(answer_count):
        # Find the start of the answer (skip past name compression and type/class)
        pos = rsp.find(b"\xc0", pos)
        if pos < 0:
            raise ValueError("Invalid DNS response")
        answer_type = _parse_int(rsp[pos + 2 : pos + 4])
        if rsp[pos + 4 : pos + 6] != b"\x00\x01":  # QCLASS (IN)
            raise ValueError("Invalid DNS response")
        # TODO: ttl = _parse_int(rsp[pos + 6 : pos + 10])
        data_length = _parse_int(rsp[pos + 10 : pos + 12])
        pos += 12
        if answer_type == 1 and data_length == 4:  # IPv4 (A record)
            ip = rsp[pos : pos + 4]
            answers.append((AF_INET, ".".join(str(b) for b in ip)))
        elif answer_type == 28 and data_length == 16:  # IPv6 (AAAA record)
            ip = rsp[pos : pos + 16]
            answers.append((AF_INET6, ":".join(f"{_parse_int(ip[i:i+2]):x}" for i in range(0, 16, 2))))
        # else:
        #    log.warning("Unknown answer %d (len:%d)", answer_type, data_length)
        pos += data_length
    return answers


def _dns_addr(x):
    return _gai(x, 53, 0, SOCK_DGRAM)[0][-1]


# Asynchronous getaddrinfo compatible function
async def getaddrinfo(host, port, family=AF_INET, type=0, proto=0, flags=0):
    host = host.lower()  # Domains are case-insensitive
    port = int(port)
    if not type:
        type = SOCK_STREAM

    # TODO: use AI_NUMERICHOST
    # See https://github.com/vshymanskyy/aiodns/issues/9
    if _ip4(host) or _ip6(host):
        return _gai(host, port, family, type, proto, flags)

    cache_key = (host, family)
    if cache_key in cache:
        # TODO: check TTL
        # Mark as most recently used
        results = cache.pop(cache_key)
        cache[cache_key] = results
        # log.debug("%s found in cache", host)
        res = []
        for fam, addr in results:
            res.extend(_gai(addr, port, fam, type, proto, flags))
        return res

    s = socket.socket(AF_INET, SOCK_DGRAM)
    s.setblocking(False)
    try:
        query_ids = []
        tout = timeout_ms
        results = []
        finished = total = 0
        t = time.ticks_ms()
        loc = host.endswith(".local")

        if loc:
            srv = [_gai("224.0.0.251", 5353, 0, SOCK_DGRAM)[0][-1]]
        else:
            srv = [_dns_addr(x) for x in servers]
            if hasattr(network, "ipconfig"):
                sysdns = network.ipconfig("dns")
                if sysdns and sysdns != "0.0.0.0":
                    srv.append(_dns_addr(sysdns))

        # Send the query to all DNS servers in parallel
        for qtype in _qtypes[family]:
            query = _build_dns_query(host, qtype)
            query_ids.append(query[0:2])
            for dns in srv:
                for retry in range(10):
                    try:
                        if s.sendto(query, dns) == len(query):
                            total += 1
                            break
                    except Exception:
                        pass
                    await sleep_ms(10)
                await sleep_ms(1)

        while (dt := time.ticks_diff(time.ticks_ms(), t)) < tout and finished < total:
            try:
                rsp, addr = s.recvfrom(256)
                if rsp[0:2] not in query_ids:  # Verify Transaction ID
                    continue
                if addr not in srv and not loc:
                    continue
                finished += 1
                answers = _parse_dns_rsp(rsp)
                # log.debug("%s responded with %s (%d ms)", addr[0], answers, dt)
                results.extend(x for x in answers if x not in results)
                # Give 50 ms for additional responses to arrive
                tout = dt + 50
            except Exception:
                await sleep_ms(5)
        if not results:
            raise OSError(f"Failed to resolve {host}")

        cache[cache_key] = results
        while len(cache) > cache_size:
            # Remove least recently used item
            cache.pop(next(iter(cache)))

        res = []
        for fam, addr in results:
            res.extend(_gai(addr, port, fam, type, proto, flags))
        return res
    finally:
        s.close()
