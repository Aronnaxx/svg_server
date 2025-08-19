#!/usr/bin/env python3
"""
Simple SVG static server with CORS for Grafana.

Usage:
  python3 server.py --dir ./svgs --host 0.0.0.0 --port 8000

This serves files from the given directory and adds CORS headers so Grafana
can fetch them from the browser.
"""
import argparse
import logging
import mimetypes
import os
import sys
import ssl
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from http.server import HTTPServer

# Ensure SVG has the correct MIME type
mimetypes.add_type('image/svg+xml', '.svg')


class CORSRequestHandler(SimpleHTTPRequestHandler):
    # Add CORS headers on all responses
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept, Range')
        # Cache for 5 minutes; adjust if you want stronger caching
        self.send_header('Cache-Control', 'public, max-age=300')
        super().end_headers()

    # Handle CORS preflight (rarely needed for simple GETs, but harmless)
    def do_OPTIONS(self):  # noqa: N802 (match BaseHTTPRequestHandler naming)
        self.send_response(204)
        self.end_headers()

    # Only allow GET/HEAD/OPTIONS
    def do_POST(self):  # noqa: N802
        self.send_error(405, 'Method Not Allowed')


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def run(directory: str, host: str, port: int, certfile: str | None = None, keyfile: str | None = None) -> None:
    # Change working directory to serve from desired folder without affecting absolute paths
    serve_dir = os.path.abspath(directory)
    if not os.path.isdir(serve_dir):
        print(f"Error: directory not found: {serve_dir}", file=sys.stderr)
        sys.exit(1)

    os.chdir(serve_dir)

    handler_class = CORSRequestHandler

    httpd = ThreadingHTTPServer((host, port), handler_class)

    scheme = "http"
    if certfile:
        # Enable TLS if certificate is provided
        if not os.path.isfile(certfile):
            print(f"Error: certfile not found: {certfile}", file=sys.stderr)
            sys.exit(2)
        if keyfile and not os.path.isfile(keyfile):
            print(f"Error: keyfile not found: {keyfile}", file=sys.stderr)
            sys.exit(2)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        scheme = "https"

    logging.info("Serving %s at %s://%s:%d", serve_dir, scheme, host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        logging.info("Server stopped")


def main():
    parser = argparse.ArgumentParser(description='Serve SVG files with CORS for Grafana')
    parser.add_argument('--dir', default='./svgs', help='Directory to serve (default: ./svgs)')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind (default: 8000)')
    parser.add_argument('--certfile', help='Path to TLS certificate (PEM). Enables HTTPS if provided.')
    parser.add_argument('--keyfile', help='Path to TLS private key (PEM). Optional if bundled with certfile.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format='[%(asctime)s] %(levelname)s: %(message)s')

    run(args.dir, args.host, args.port, certfile=args.certfile, keyfile=args.keyfile)


if __name__ == '__main__':
    main()
