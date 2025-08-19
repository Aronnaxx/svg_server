# SVG Static Server for Grafana

This tiny Python server hosts a folder of SVGs with permissive CORS so Grafana panels can fetch them via URL.

## Quick start

1) Ensure Python 3.8+ is installed.

2) Start the server (serves the `svgs/` folder by default):

```
python3 server.py --dir ./svgs --host 0.0.0.0 --port 8000
```

3) Test locally in a browser:
- http://localhost:8000/hello.svg

4) Use in Grafana
- In panels/plugins that accept image URLs, reference your SVG like:
  - http://YOUR_MACHINE_IP:8000/your.svg
- Make sure Grafana can reach your machine (same network / firewall rules allow port 8000).

## Notes
- CORS is set to `*` so Grafana can fetch from the browser.
- MIME type for `.svg` is explicitly registered as `image/svg+xml`.
- Edit cache duration by changing the `Cache-Control` header in `server.py` if you want more aggressive caching.
- Folder listing is enabled by default (inherited from Python's SimpleHTTPRequestHandler).
