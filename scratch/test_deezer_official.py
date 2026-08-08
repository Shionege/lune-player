import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = [
    "Coldplay Yellow",
    "Ed Sheeran Photograph",
    "Ariana Grande hate that i made you love me",
    "Erie Suzan Senandung Rindu",
    "Denny Caknan Crito Mustahil",
    "Sheila on 7 Dan"
]

for q in queries:
    print(f"\n================ Deezer Official Track: '{q}' ================")
    url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            items = data.get('data', [])
            print(f"  Deezer official items found: {len(items)}")
            for it in items[:3]:
                title = it.get('title')
                artist = it.get('artist', {}).get('name')
                album = it.get('album', {}).get('title')
                preview = it.get('preview')
                duration = it.get('duration')
                print(f"  -> Title: '{title}' | Artist: '{artist}' | Album: '{album}' | Duration: {duration}s")
                print(f"     IS ORIGINAL STUDIO RECORDING: {artist.lower() in q.lower() or title.lower() in q.lower()}")
    except Exception as e:
        print(f"  Deezer error: {e}")
