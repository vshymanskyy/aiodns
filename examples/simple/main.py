import asyncio
import socket
import aiodns

WIFI_SSID = ""
WIFI_PASS = ""

async def connect_sta():
    import network
    if not hasattr(network, "WLAN"):
        return
    if not WIFI_SSID:
        raise ValueError("WIFI_SSID and WIFI_PASS not configured")
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
        for a in addr:
            print(a)
        sock = socket.socket(family, socket.SOCK_STREAM)
        print("Connecting...")
        sock.connect(addr[0][-1])
        sock.close()
        print("Connection OK")
    except Exception as e:
        print("Connection Failed.", e)

async def run_example(hostname):
    await connect_sta()
    print("=== IPv4 ===")
    await test_connection(hostname, aiodns.AF_INET)
    print("=== IPv6 ===")
    await test_connection(hostname, aiodns.AF_INET6)

if __name__ == "__main__":
    asyncio.run(run_example("google.com"))
