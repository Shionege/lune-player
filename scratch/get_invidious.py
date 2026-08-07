import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://api.invidious.io/instances.json?sort_by=health"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        data = json.loads(res.read().decode('utf-8'))
        valid = []
        for domain, info in data:
            if info.get('type') == 'https' and info.get('cors'):
                valid.append(info.get('uri'))
        print("Healthy CORS Invidious Instances:", valid[:5])
except Exception as e:
    print("Err:", e)
