import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

endpoints = [
    "https://saavn.dev/api/search/songs?query=",
    "https://saavn.me/api/search/songs?query=",
    "https://jiosaavn-api-v3.vercel.app/search?query=",
    "https://jiosaavn-api-v3.vercel.app/api/search/songs?query=",
    "https://saavn-api-murex.vercel.app/search/songs?query="
]

queries = ["Photograph Ed Sheeran", "Yellow Coldplay", "Erie Suzan", "Nasida Ria", "Denny Caknan"]

for q in queries:
    print(f"\n================ Search: '{q}' ================")
    for ep in endpoints:
        url = ep + urllib.parse.quote(q)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    raw = res.read().decode('utf-8')
                    try:
                        data = json.loads(raw)
                        results = data.get('data', {}).get('results', []) or data.get('results', [])
                        if results:
                            s = results[0]
                            name = s.get('name') or s.get('title')
                            urls = s.get('downloadUrl', []) or s.get('media_url', '')
                            print(f"  SUCCESS [{ep[:35]}]: Song '{name}' | Audio: {str(urls)[:100]}...")
                            break
                    except Exception as e:
                        pass
        except Exception as e:
            pass
