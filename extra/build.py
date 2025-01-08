#!/usr/bin/env python
import python_minifier
import mpy_cross
from subprocess import PIPE

def minify(code):
    return python_minifier.minify(code,
        rename_globals=True,
        preserve_globals=[
            "getaddrinfo",
            "servers",
            "cache",
            "cache_size",
            "timeout_ms",
            "AF_INET",
            "AF_INET6",
            "AF_UNSPEC",
            "SOCK_DGRAM",
            "SOCK_STREAM",
        ]
    )

def mpycompile(code, filename="<stdin>"):
    proc = mpy_cross.run(
        "-O3", "-s", filename, "-",
        stdin=PIPE, stdout=PIPE, stderr=PIPE,
    )
    stdout, stderr = proc.communicate(input=code.encode())
    if proc.returncode == 0:
        return stdout
    else:
        raise Exception(stderr.decode())

if __name__ == "__main__":
    with open("aiodns.py") as f:
        src = f.read()

    with open("extra/aiodns.min.py", "w") as f:
        d = minify(src)
        f.write(d)
        print(f"Minified: {len(d)} bytes")

    with open("extra/aiodns.mpy", "wb") as f:
        d = mpycompile(src, "aiodns.py")
        f.write(d)
        print(f"Compiled: {len(d)} bytes")
