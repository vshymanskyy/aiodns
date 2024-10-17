import network
import asyncio
import socket
import aiodns
from aiodns import AF_INET, AF_INET6

WIFI_SSID = ""
WIFI_PASS = ""

async def connect_sta():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Connecting to WiFi...")
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASS)
        while not sta_if.isconnected():
            await asyncio.sleep_ms(10)

async def test_connection(hostname, family):
    try:
        addr = await aiodns.getaddrinfo(hostname, 80, family)
        print("Address info:", addr)
        sock = socket.socket(family, socket.SOCK_STREAM)
        print("Connecting...")
        sock.connect(addr[0][-1])
        sock.close()
        print("Connection OK")
    except Exception:
        print("Connection Failed")

async def run_example(hostname):
    if not WIFI_SSID:
        print("WIFI_SSID and WIFI_PASS not configured")
        return
    await connect_sta()
    print("=== IPv4 ===")
    await test_connection(hostname, AF_INET)
    print("=== IPv6 ===")
    await test_connection(hostname, AF_INET6)

if __name__ == "__main__":
    asyncio.run(run_example("google.com"))
