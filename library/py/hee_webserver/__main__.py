#!/usr/bin/env python3
import argparse
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="generated/html", help="document root (default generated/html)")
    ap.add_argument("--bind", default="127.0.0.1", help="bind addr (default 127.0.0.1)")
    ap.add_argument("--port", type=int, default=8000, help="port (default 8000; use 0 for auto)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"root_missing={root}")
        return 2

    os.chdir(root)
    httpd = ThreadingHTTPServer((args.bind, args.port), SimpleHTTPRequestHandler)
    host, port = httpd.server_address
    print(f"url=http://{host}:{port}/ root={root}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
