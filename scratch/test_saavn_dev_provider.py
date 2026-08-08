import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test saavn.dev and audiomack and freemusicarchive
endpoints = [
    "https://saavn.dev/api/search/songs?query=",
    "https://jiosaavn-api-v3.vercel.app/search?query="
]

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil", "Sheila on 7 Dan"]

for q in queries:
    print(f"\n================ Target: '{q}' ================")
    for ep in endpoints:
        try:
            url = ep + urllib.parse.quote(q)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    results = data.get('data', {}).get('results', []) or data.get('results', [])
                    if results:
                        print(f"  [saavn.dev API] Found {len(results)} official studio tracks!")
                        for r in results[:2]:
                            title = str(r.get('name') or r.get('title')).encode('ascii', 'ignore').decode('ascii')
                            artist = str(r.get('primaryArtists') or r.get('singers')).encode('ascii', 'ignore').decode('ascii')
                            d_urls = r.get('downloadUrl')
                            if isinstance(d_urls, list) and d_urls:
                                print(f"    -> Title: '{title}' by '{artist}' | Direct 320kbps MP3: {d_urls[-1].get('url')[:70]}...")
                            elif isinstance(r.get('media_url'), str):
                                print(f"    -> Title: '{title}' by '{artist}' | Direct Media URL: {r.get('media_url')[:70]}...")
                        break
        except Exception as e:
            pass
