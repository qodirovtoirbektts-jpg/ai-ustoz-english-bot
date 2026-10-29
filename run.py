#!/usr/bin/env python3
"""Root runner for AI Ustoz English Telegram Bot."""
import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from bot.main import main


def start_health_server() -> None:
    """Optional health check server when running on cloud platforms (e.g. Render)."""
    port_str = os.environ.get("PORT")
    if not port_str:
        return

    try:
        port = int(port_str)
    except ValueError:
        return

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"AI Ustoz English Bot is running OK.")

        def log_message(self, format, *args):
            pass

    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()


def start_keep_alive_pinger() -> None:
    """Keep free Render web service awake 24/7 by pinging self every 10 minutes."""
    import time
    import urllib.request

    def ping_worker():
        time.sleep(180)
        while True:
            target_url = os.environ.get("RENDER_EXTERNAL_URL") or os.environ.get("SELF_PING_URL")
            if target_url:
                try:
                    req = urllib.request.Request(target_url, headers={"User-Agent": "RenderKeepAlive/1.0"})
                    urllib.request.urlopen(req, timeout=15)
                except Exception:
                    pass
            time.sleep(600)

    thread = threading.Thread(target=ping_worker, daemon=True)
    thread.start()


if __name__ == "__main__":
    start_health_server()
    start_keep_alive_pinger()
    asyncio.run(main())
