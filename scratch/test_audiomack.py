import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test search query "Ed Sheeran Photograph" on Audiomack, SoundCloud, Deezer, Archive.org
queries = ["Ed Sheeran Photograph", "Coldplay Yellow", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir"]

# Test Audiomack API
for q in queries:
    print(f"\n================ Audiomack test: '{q}' ================")
    url = f"https://api.audiomack.com/v1/search?q={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            results = data.get('results', [])
            print(f"  Audiomack results count: {len(results)}")
            if results:
                s = results[0]
                print(f"  -> Title: {s.get('title')} | Artist: {s.get('artist')} | URL: {s.get('url')}")
    except Exception as e:
        print(f"  Audiomack error: {e}")
