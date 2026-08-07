import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://aac.saavncdn.com/263/XI13sFFOXjkVqvHpnd0KRumQyQUPYMqf_160.mp4"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
    print("Saavn Audio Direct URL Status:", res.status)
    print("Content-Length:", res.headers.get('Content-Length'))
    print("Content-Type:", res.headers.get('Content-Type'))
    print("Access-Control-Allow-Origin:", res.headers.get('Access-Control-Allow-Origin'))
