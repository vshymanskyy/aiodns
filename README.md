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

```py
import aiodns
# Connect your board to any network
info = await aiodns.getaddrinfo("google.com", 443)
print(info)
```

## API

```py
set_servers(["8.8.8.8", "1.1.1.1"])
add_server("9.9.9.9")
set_timeout_ms(5000)
clear_cache()
async getaddrinfo(hostname, port, family=AF_INET, type=0, proto=0, flags=0)
```
