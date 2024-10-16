import network
import asyncio
import aiodns

WIFI_SSID = ""
WIFI_PASS = ""


async def connect_sta():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Connecting to WiFi...")
        if not WIFI_SSID:
            raise Exception("WIFI_SSID and WIFI_PASS not configured")
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASS)
        while not sta_if.isconnected():
            await asyncio.sleep_ms(10)
    # Add local DNS to aiodns
    aiodns.add_server(sta_if.ifconfig()[3])


async def run_example():
    await connect_sta()
    info = await aiodns.getaddrinfo("google.com", 443)
    print(info)


if __name__ == "__main__":
    asyncio.run(run_example())