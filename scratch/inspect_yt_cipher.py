import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

vids = ['tdVAqxNLXiw', 'KKQl-pIRQMY', 'XMvKTY_0Eks', 'jhAHUF_40zk']

for vid in vids:
    print(f"\n================ Video ID: {vid} ================")
    url = f"https://www.youtube.com/watch?v={vid}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        html = res.read().decode('utf-8')
        m = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});var', html) or re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});</script>', html)
        if m:
            pdata = json.loads(m.group(1))
            formats = pdata.get('streamingData', {}).get('adaptiveFormats', [])
            for f in formats:
                if f.get('mimeType', '').startswith('audio/'):
                    url_val = f.get('url')
                    cipher_val = f.get('signatureCipher') or f.get('cipher')
                    print(f"  Audio Format: mime={f.get('mimeType')[:25]} | URL present: {bool(url_val)} | Cipher present: {bool(cipher_val)}")
                    if url_val:
                        print(f"    -> DIRECT URL: {url_val[:80]}...")
