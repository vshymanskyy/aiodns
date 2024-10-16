# SPDX-FileCopyrightText: 2024 Volodymyr Shymanskyy
# SPDX-License-Identifier: MIT
#
# The software is provided "as is", without any warranties or guarantees (explicit or implied).
# This includes no assurances about being fit for any specific purpose.

__copyright__ = "2024 Volodymyr Shymanskyy"
__license__ = "MIT"
__version__ = "0.1.1"

import time
import os
from socket import socket, AF_INET, AF_INET6, SOCK_DGRAM, SOCK_STREAM
from collections import OrderedDict
from asyncio import sleep_ms

# import logging
# log = logging.getLogger(__name__)

# Define DNS servers to query (Google, Cloudflare, Quad9)
_servers = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
_timeout = 5000

_cache = OrderedDict()
_cache_size = 32
_qtypes = {
    AF_INET: (b"\x00\x01",),  # A
    AF_INET6: (b"\x00\x1c",),  # AAAA
    0: (b"\x00\x01", b"\x00\x1c"),
}


def _build_dns_query(hostname, qtype):
    hostname = hostname.encode()
    query = bytearray(17 + len(hostname))  # Header + Hostname + NULL + (Questions * 4)
    query[0:2] = os.urandom(2)  # Transaction ID
    query[2:4] = b"\x01\x00"  # Standard query with recursion desired
    query[4:6] = b"\x00\x01"  # Questions count = 1
    # query[6:12] => Answer RRs, Authority RRs, Additional RRs (all set to 0)
    pos = 12
    for part in hostname.split(b"."):  # QNAME (hostname in DNS format)
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
    return int.from_bytes(b, 'big')


def _parse_dns_response(response):
    if len(response) < 12:
        raise ValueError("Invalid DNS response")

    answer_count = _parse_int(response[6:8])
    if not answer_count:
        raise ValueError("Invalid DNS response")

    answers = []
    pos = 12
    for _ in range(answer_count):
        # Find the start of the answer (skip past name compression and type/class)
        pos = response.find(b"\xc0", pos)
        if pos < 0:
            raise ValueError("Invalid DNS response")
        answer_type = _parse_int(response[pos + 2 : pos + 4])
        if response[pos + 4 : pos + 6] != b"\x00\x01":  # QCLASS (IN)
            raise ValueError("Invalid DNS response")
        # TODO: ttl = _parse_int(response[pos + 6 : pos + 10])
        data_length = _parse_int(response[pos + 10 : pos + 12])
        pos += 12
        if answer_type == 1 and data_length == 4:  # IPv4 (A record)
            ip = response[pos : pos + 4]
            answers.append((AF_INET, ".".join(str(b) for b in ip)))
        elif answer_type == 28 and data_length == 16:  # IPv6 (AAAA record)
            ip = response[pos : pos + 16]
            answers.append((AF_INET6, ":".join(f"{_parse_int(ip[i:i+2]):x}" for i in range(0, 16, 2))))
        # else:
        #    log.warning("Unknown answer %d (len:%d)", answer_type, data_length)
        pos += data_length
    return answers


def set_servers(s):
    _servers = list(set(s))  # accept unique addresses


def add_server(addr):
    if addr not in _servers:
        _servers.insert(0, addr)


def set_timeout_ms(ms):
    _timeout = ms


def clear_cache():
    _cache.clear()


# Asynchronous getaddrinfo compatible function
async def getaddrinfo(hostname, port, family=AF_INET, type=0, proto=0, flags=0):
    hostname = hostname.lower()  # Domains are case-insensitive
    if not type:
        type = SOCK_STREAM

    cache_key = (hostname, family)
    if cache_key in _cache:
        # TODO: check TTL
        # Mark as most recently used
        results = _cache.pop(cache_key)
        _cache[cache_key] = results
        # log.debug("%s found in cache", hostname)
        return [(fam, type, proto, "", (addr, port)) for fam, addr in results]

    try:
        query_ids = []
        tout = _timeout
        results = []
        finished = total = 0
        t = time.ticks_ms()

        # Send the query to all DNS servers in parallel
        s = socket(AF_INET, SOCK_DGRAM)
        s.setblocking(False)
        for qtype in _qtypes[family]:
            query = _build_dns_query(hostname, qtype)
            query_ids.append(query[0:2])
            for dns in _servers:
                for retry in range(10):
                    try:
                        if s.sendto(query, (dns, 53)) == len(query):
                            total += 1
                            break
                    except Exception:
                        pass
                    await sleep_ms(10)
                await sleep_ms(1)

        while (dt := time.ticks_diff(time.ticks_ms(), t)) < tout and finished < total:
            try:
                rsp, addr = s.recvfrom(512)
                finished += 1
                if rsp[0:2] not in query_ids:  # Verify Transaction ID
                    continue
                # TODO: check if the response comes from the server we contacted
                answers = _parse_dns_response(rsp)
                # log.debug("%s responded with %s (%d ms)", addr[0], answers, dt)
                results.extend(x for x in answers if x not in results)
                # Give 50 ms for additional responses to arrive
                tout = time.ticks_add(dt, 50)
            except Exception:
                await sleep_ms(5)
        if not results:
            raise OSError(f"Failed to resolve {hostname}")

        _cache[cache_key] = results
        while len(_cache) > _cache_size:
            # Remove least recently used item
            _cache.pop(next(iter(_cache)))
        return [(fam, type, proto, "", (addr, port)) for fam, addr in results]
    finally:
        s.close()
