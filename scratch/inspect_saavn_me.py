import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://saavn.me/api/search/songs?query=Coldplay+Yellow"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        print("Status:", res.status)
        raw = res.read().decode('utf-8')
        print("Raw first 200 chars:", raw[:200])
except Exception as e:
    print("Err:", e)
