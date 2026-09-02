#!/usr/bin/env python3
"""Start een lokale webserver en open het dashboard in de browser.

Gebruik:
    python3 scripts/serve.py

Nodig omdat het dashboard `data/items.json` via fetch() ophaalt; dat werkt niet
als je het HTML-bestand rechtstreeks opent (file://), wel via http://localhost.
Stoppen met Ctrl+C.
"""
import http.server
import socketserver
import webbrowser
from functools import partial
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PORT = 8000

if __name__ == "__main__":
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(PROJECT_ROOT))
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}/dashboard/"
        print(f"Dashboard draait op {url}  (Ctrl+C om te stoppen)")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nGestopt.")
