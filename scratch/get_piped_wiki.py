import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://raw.githubusercontent.com/wiki/TeamPiped/Piped-Frontend/Instances.md"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        raw = res.read().decode('utf-8')
        import re
        apis = re.findall(r'https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw)
        print("Found APIs:", list(set(apis))[:10])
except Exception as e:
    print("Err:", e)
