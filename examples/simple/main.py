import network
import asyncio
import aiodns

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


async def main():
    await connect_sta()
    info = await aiodns.getaddrinfo("google.com", 443)
    print(info)


if __name__ == "__main__":
    asyncio.run(main())
