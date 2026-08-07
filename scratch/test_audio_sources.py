import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Erie Suzan Senandung Rindu", "Ed Sheeran Photograph", "Coldplay Yellow", "Taylor Swift Blank Space"]

test_urls = [
    # JioSaavn alternative public APIs
    "https://jiosaavn-api-v3.vercel.app/search?query=",
    "https://saavn.me/api/search/songs?query=",
    "https://jiosaavn-api.vercel.app/search?query=",
    # Invidious / YouTube Audio APIs
    "https://inv.tux.pizza/api/v1/search?q=",
    "https://invidious.nerdvpn.de/api/v1/search?q=",
    "https://api.piped.video/search?q="
]

for q in queries:
    print(f"\n================ Target query: '{q}' ================")
    for endpoint in test_urls:
        url = endpoint + urllib.parse.quote(q)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    raw = res.read().decode('utf-8')
                    try:
                        data = json.loads(raw)
                        print(f"  [200 OK] {endpoint[:35]} -> Data type: {type(data)}, keys/len: {len(data) if isinstance(data, list) else list(data.keys())[:5]}")
                    except Exception as je:
                        print(f"  [200 Non-JSON] {endpoint[:35]} -> Raw len: {len(raw)}")
        except Exception as e:
            print(f"  [ERROR] {endpoint[:35]} -> {e}")
