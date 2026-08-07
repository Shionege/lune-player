import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://piped-instances.kavin.rocks/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        data = json.loads(res.read().decode('utf-8'))
        working = [i['api_url'] for i in data if i.get('up') and i.get('name')]
        print("Working Piped Instances:", working[:5])
except Exception as e:
    print("Err:", e)
