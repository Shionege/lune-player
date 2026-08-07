import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.youtube.com/watch?v=XMvKTY_0Eks"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
    html = res.read().decode('utf-8')
    m = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});var', html) or re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});</script>', html)
    if m:
        pdata = json.loads(m.group(1))
        formats = pdata.get('streamingData', {}).get('adaptiveFormats', [])
        for f in formats:
            if f.get('mimeType', '').startswith('audio/'):
                print("Format keys:", list(f.keys()))
                print("Sample format obj:", json.dumps(f, indent=2)[:300])
                break
