import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://jiosaavn-api-v3.vercel.app/search?query=Senandung+Rindu+Erie+Suzan"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        data = json.loads(res.read().decode('utf-8'))
        print("Saavn V3 Response:", json.dumps(data, indent=2)[:500])
except Exception as e:
    print("Error:", e)
