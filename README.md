# aiodns

[![StandWithUkraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/StandWithUkraine.svg)](https://github.com/vshymanskyy/StandWithUkraine/blob/main/docs/README.md) 
[![GitHub issues](https://img.shields.io/github/issues-raw/vshymanskyy/aiodns?style=flat-square&label=issues&color=green)](https://github.com/vshymanskyy/aiodns/issues) 
[![GitHub license](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](https://github.com/vshymanskyy/aiodns) 
[![Support vshymanskyy](https://img.shields.io/static/v1?label=support&message=%E2%9D%A4&color=%23fe8e86)](https://quicknote.io/da0a7d50-bb49-11ec-936a-6d7fd5a2de08) 

<!-- [![Build status](https://img.shields.io/github/actions/workflow/status/vshymanskyy/aiodns/static.yml?branch=main&style=flat-square&logo=github&label=build)](https://github.com/vshymanskyy/aiodns/actions) -->
<!--[![GitHub Repo stars](https://img.shields.io/github/stars/vshymanskyy/aiodns?style=flat-square&color=green)](https://github.com/vshymanskyy/aiodns/stargazers) -->

A small async DNS client for MicroPython

- Works on `ESP32`, `ESP8266`, `Raspberry Pi Pico W`, `WM W600` and other boards
- Versatile, runs multiple queries at a time using multiple DNS servers
- Supports IPv4 and IPv6
- Supports `mDNS` (Multicast DNS) name resolution
- Works with WiFi, Ethernet, Cellular, and in multi-network scenarios
- Caches up to 32 hostnames (configurable)
- API-compatible with `getaddrinfo`

## Install

[<img src="https://raw.githubusercontent.com/vshymanskyy/ViperIDE/refs/heads/main/assets/btn_install.png" alt="Install using ViperIDE" height="42"/>](https://viper-ide.org/?install=github:vshymanskyy/aiodns)

Using CLI:

```sh
mpremote mip install github:vshymanskyy/aiodns
```

Using REPL (your board must be connected to the internet):

```py
import mip
mip.install("github:vshymanskyy/aiodns")
```

## Example

See [usage examples](./examples)

## API

```py
aiodns.servers = set(["8.8.8.8", "1.1.1.1"])
aiodns.servers.add("9.9.9.9")
aiodns.timeout_ms = 5000
aiodns.cache.clear()
aiodns.cache_size = 32
await aiodns.getaddrinfo(hostname, port, family=AF_INET, type=0, proto=0, flags=0)
```

## Extra

Minify to ~`2'800` bytes:

```sh
pip3 install -U python-minifier
pyminify aiodns.py -o aiodns_min.py --rename-globals --preserve-globals=getaddrinfo,servers,cache,cache_size,timeout_ms,AF_INET,AF_INET6,AF_UNSPEC,SOCK_DGRAM,SOCK_STREAM
```

Compile to MPY ~`2'200` bytes:

```sh
mpy-cross aiodns.py -O3 -o aiodns.mpy
```

Run example using MicroPython Unix port:

```sh
export MICROPYPATH=".frozen:."
micropython examples/simple/main.py
```
