import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test additional YouTube Music endpoints & free stream APIs
queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Denny Caknan Crito Mustahil"]

additional_endpoints = [
    "https://pipedapi.tokhmi.xyz",
    "https://pipedapi.resonate.edu.au",
    "https://pipedapi.syncv.xyz",
    "https://pipedapi.mha.fi",
    "https://inv.riverside.rocks",
    "https://invidious.projectsegfau.lt",
    "https://invidious.flokinet.to",
    "https://vid.puffyan.us"
]

for q in queries:
    print(f"\n================ Target: '{q}' ================")
    for ep in additional_endpoints:
        try:
            url = f"{ep}/search?q={urllib.parse.quote(q)}&filter=music_songs" if 'piped' in ep else f"{ep}/api/v1/search?q={urllib.parse.quote(q)}&type=video"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    items = data.get('items', []) if isinstance(data, dict) else data
                    if items:
                        print(f"  [{ep}] Found {len(items)} items!")
                        top = items[0]
                        v_id = top.get('videoId') or top.get('url', '').replace('/watch?v=', '')
                        title = str(top.get('title')).encode('ascii', 'ignore').decode('ascii')
                        print(f"    -> YouTube Title: '{title}' (ID: {v_id})")
                        break
        except Exception as e:
            pass
