import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir", "Coldplay Yellow", "Ed Sheeran Photograph"]

for q in queries:
    print(f"\nSearching Jamendo: '{q}'")
    url = f"https://api.jamendo.com/v3.0/tracks/?client_id=56d30c95&format=json&limit=3&namesearch={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        data = json.loads(res.read().decode('utf-8'))
        results = data.get('results', [])
        print(f"  Count: {len(results)}")
        for tr in results:
            print(f"  -> Title: {tr.get('name')} | Artist: {tr.get('artist_name')} | Audio: {tr.get('audio')}")
