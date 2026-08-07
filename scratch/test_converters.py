import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

vids = ['WJ9F2qiw3wg', 'C8l-A7HxXmY', '2P4WT0b0myo', '6sKRBRSUego']

for v in vids:
    print(f"\nVideo ID: {v}")
    yt_url = f"https://www.youtube.com/watch?v={v}"
    
    # Try YtMp3 / Y2Mate / loaders
    apis = [
        ("https://api.cobalt.tools", json.dumps({"url": yt_url}).encode('utf-8')),
        ("https://v3.y2mate.is/api/convert", json.dumps({"url": yt_url}).encode('utf-8')),
    ]
    
    for endpoint, payload in apis:
        try:
            req = urllib.request.Request(
                endpoint,
                data=payload,
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
                print(f"  Response {endpoint}: {res.status} -> {res.read().decode('utf-8')[:120]}")
        except Exception as e:
            print(f"  Err {endpoint}: {e}")
