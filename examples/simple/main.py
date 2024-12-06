import asyncio
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

async def resolve(hostname, family):
    try:
        addr = await aiodns.getaddrinfo(hostname, 80, family)
        for a in addr:
            print("   ", a)
        return addr[0][-1]
    except Exception as e:
        print("    Resolving Failed.", e)

async def test(hostname):
    print("=== Resolving", hostname, "===")
    print("  IPv4:")
    await resolve(hostname, aiodns.AF_INET)
    print("  IPv6:")
    await resolve(hostname, aiodns.AF_INET6)
    #print("  UNSPEC:")
    #await resolve(hostname, aiodns.AF_UNSPEC)

async def main():
    await connect_sta()
    await test("google.com")                        # Regular DNS
    #await test("mdns-test.local")                  # Multicast DNS (mDNS)
    await test("127.0.0.1")                         # Numeric IPv4
    await test("2001:db8:85a3::8a2e:370:7334")      # Numeric IPv6

if __name__ == "__main__":
    asyncio.run(main())
