#!/usr/bin/env python3
"""Root runner for AI Ustoz English Telegram Bot."""
import asyncio
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Unbuffered output for real-time cloud logging
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True)


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

    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"Health server successfully started on port {port}")
    except Exception as e:
        print(f"Health server failed to start: {e}", file=sys.stderr)


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

    try:
        thread = threading.Thread(target=ping_worker, daemon=True)
        thread.start()
    except Exception as e:
        print(f"Keep-alive pinger error: {e}", file=sys.stderr)


if __name__ == "__main__":
    from bot.main import main

    start_health_server()
    start_keep_alive_pinger()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Shutdown requested.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
