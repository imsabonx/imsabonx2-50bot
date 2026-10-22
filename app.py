import os
import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
MAX_WORKERS = 50
TIMEOUT_SECONDS = 12
MAX_URLS_PER_BATCH = 200

# Set this on your hosting provider, e.g.:
# ALLOWED_DOMAINS=example.com,www.example.com
ALLOWED_DOMAINS = {
    item.strip().lower()
    for item in os.environ.get("ALLOWED_DOMAINS", "").split(",")
    if item.strip()
}

def domain_is_allowed(host):
    host = (host or "").lower().rstrip(".")
    if not host or not ALLOWED_DOMAINS:
        return False
    return any(host == d or host.endswith("." + d) for d in ALLOWED_DOMAINS)

def has_public_dns(host):
    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        ips = {ipaddress.ip_address(info[4][0]) for info in infos}
        return bool(ips) and all(ip.is_global for ip in ips)
    except (OSError, ValueError):
        return False

def check_url(url):
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return {"url": url, "status": "Rejected", "detail": "Only valid HTTPS URLs are accepted."}
    if parsed.username or parsed.password:
        return {"url": url, "status": "Rejected", "detail": "URLs containing credentials are not accepted."}
    host = parsed.hostname.lower().rstrip(".")
    if not domain_is_allowed(host):
        return {"url": url, "status": "Rejected", "detail": "Domain is not in ALLOWED_DOMAINS. Configure your approved domains on the server."}
    if not has_public_dns(host):
        return {"url": url, "status": "Rejected", "detail": "DNS failed or host did not resolve exclusively to public IP addresses."}

    try:
        # Redirects are intentionally disabled to avoid following unapproved destinations.
        response = requests.get(
            url,
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,
            stream=True,
            headers={"User-Agent": "SabonX2-Link-Checker/1.0"}
        )
        code = response.status_code
        response.close()
        reachable = 200 <= code < 400
        return {
            "url": url,
            "status": "Reachable" if reachable else "Failed",
            "http_status": code,
            "detail": "HTTP response received. This verifies reachability only, not completion of a task."
        }
    except requests.RequestException as exc:
        return {"url": url, "status": "Failed", "detail": type(exc).__name__}

@app.get("/")
def index():
    return render_template("index.html", allowlist_configured=bool(ALLOWED_DOMAINS))

@app.post("/api/check")
def api_check():
    data = request.get_json(silent=True) or {}
    raw_urls = data.get("urls", "")
    if not isinstance(raw_urls, str):
        return jsonify({"error": "urls must be text"}), 400
    urls = list(dict.fromkeys(line.strip() for line in raw_urls.splitlines() if line.strip()))
    if not urls:
        return jsonify({"error": "Add at least one URL."}), 400
    if len(urls) > MAX_URLS_PER_BATCH:
        return jsonify({"error": f"Maximum {MAX_URLS_PER_BATCH} URLs per batch."}), 400

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(check_url, url): url for url in urls}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception:
                results.append({"url": futures[future], "status": "Failed", "detail": "Unexpected checker error."})

    # Preserve the user's input order.
    order = {url: i for i, url in enumerate(urls)}
    results.sort(key=lambda row: order.get(row["url"], 10**9))
    return jsonify({
        "total": len(results),
        "reachable": sum(r["status"] == "Reachable" for r in results),
        "failed": sum(r["status"] == "Failed" for r in results),
        "rejected": sum(r["status"] == "Rejected" for r in results),
        "results": results
    })

@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "SabonX2 Link Checker"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
