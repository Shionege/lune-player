import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://inv.zoomerville.com/api/v1/search?q=Coldplay+Yellow"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        print("Status:", res.status)
        data = json.loads(res.read().decode('utf-8'))
        print("Results count:", len(data))
        if data:
            print("First vid:", data[0].get('title'), "ID:", data[0].get('videoId'))
except Exception as e:
    print("Err:", e)
