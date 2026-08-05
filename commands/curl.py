#~curl command

import os
import sys
import subprocess
import shutil
import urllib.request

def run(term, args):
    if not args:
        term.write("Usage: curl <url> [options]")
        return

    # 1. try system curl.exe (handles flags like -i, -v, -s, auto-prefixed URLs)
    curl_bin = shutil.which("curl.exe") or shutil.which("curl")
    if curl_bin and os.path.exists(curl_bin):
        try:
            cmd = [curl_bin] + list(args)
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if proc.stdout:
                term.write(proc.stdout, False)
            if proc.stderr:
                term.write(proc.stderr, False)
            return
        except Exception:
            pass

    # 2. urllib fallback with auto https:// prefixing
    url = args[0]
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    try:
        term.write(f"Fetching {url}...", False)
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read().decode("utf-8", errors="ignore")
            term.write(data, False)
    except Exception as e:
        term.write(f"curl error: {e}", False)