# -*- coding: utf-8 -*-
"""Мини-сервер для просмотра галереи: python3 tools/serve.py [порт]

Отдаёт весь репозиторий с корня, а «/» переносит на /preview/index.html,
чтобы относительные ссылки на картинки в галерее работали как надо.
Многопоточный: галерея грузит сразу несколько десятков PNG.
"""
import http.server
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def _redirect_root(self, head=False):
        if self.path in ("/", "/index.html", ""):
            self.send_response(302)
            self.send_header("Location", "/preview/index.html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return True
        return False

    def do_GET(self):
        if self._redirect_root():
            return
        super().do_GET()

    def do_HEAD(self):
        if self._redirect_root(head=True):
            return
        super().do_HEAD()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        # .sb3 и архивы — сразу на скачивание, а не открытием в браузере
        if self.path.lower().split("?")[0].endswith((".sb3", ".zip")):
            name = os.path.basename(self.path.split("?")[0])
            self.send_header("Content-Disposition", f'attachment; filename="{name}"')
        super().end_headers()

    def log_message(self, *a):
        pass


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    with Server(("0.0.0.0", PORT), Handler) as httpd:
        print(f"галерея: http://0.0.0.0:{PORT}/  →  /preview/index.html", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
