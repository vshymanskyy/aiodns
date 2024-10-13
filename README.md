# aiodns
A small async DNS client for MicroPython

- Works on `ESP32`, `Raspberry Pi Pico W`, `WM W600` and other boards
- Versatile, runs multiple queries at a time using multiple DNS servers
- Supports IPv4 and IPv6
- Caches up to 32 hostnames (configurable)
- API-compatible with `getaddrinfo`

## Install

```sh
mpremote mip install github:vshymanskyy/aiodns
```

## Example

```py
info = await getaddrinfo("google.com", 443)
print(info)
```
