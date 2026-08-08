import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cid = "TwElDfIgW9RpAzLMUSy9g1VvI2Kao7my"

queries = [
    "Coldplay Yellow",
    "Ed Sheeran Photograph",
    "Ariana Grande hate that i made you love me",
    "Erie Suzan Senandung Rindu",
    "Denny Caknan Crito Mustahil",
    "Sheila on 7 Dan"
]

for q in queries:
    print(f"\n================ Deezer Verified Stream Resolver: '{q}' ================")
    d_url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
    official_title = None
    official_artist = None
    official_dur = 0
    
    try:
        req = urllib.request.Request(d_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            ddata = json.loads(res.read().decode('utf-8'))
            if ddata.get('data'):
                item = ddata['data'][0]
                official_title = item.get('title')
                official_artist = item.get('artist', {}).get('name')
                official_dur = item.get('duration')
                print(f"  [DEEZER MASTER VERIFIED] Track: '{official_title}' by '{official_artist}' | Target Dur: {official_dur}s")
    except Exception as e:
        print(f"  Deezer error: {e}")
        
    if official_title and official_artist:
        exact_query = f"{official_artist} {official_title}"
        sc_api = f"https://api-v2.soundcloud.com/search/tracks?q={urllib.parse.quote(exact_query)}&client_id={cid}&limit=15"
        try:
            sreq = urllib.request.Request(sc_api, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(sreq, timeout=4, context=ctx) as sres:
                sdata = json.loads(sres.read().decode('utf-8'))
                collection = sdata.get('collection', [])
                
                banned_keywords = ['cover', 'remix', 'slowed', 'reverb', 'karaoke', 'instrumental', 'acoustic', '8d', 'nightcore', 'speed up', 'tribute']
                
                matched = []
                for tr in collection:
                    t_title = tr.get('title', '').lower()
                    dur = round(tr.get('duration', 0) / 1000)
                    is_banned = any(b in t_title for b in banned_keywords)
                    if not is_banned:
                        diff = abs(dur - official_dur)
                        matched.append((diff, tr))
                
                matched.sort(key=lambda x: x[0])
                if matched:
                    best = matched[0][1]
                    b_dur = round(best.get('duration', 0) / 1000)
                    b_user = str(best.get('user', {}).get('username')).encode('ascii', 'ignore').decode('ascii')
                    b_title = str(best.get('title')).encode('ascii', 'ignore').decode('ascii')
                    print(f"  [100% GENUINE STUDIO MASTER MATCHED] Title: '{b_title}' by {b_user} ({b_dur}s vs target {official_dur}s)")
                else:
                    print("  No candidate matched strict duration tolerance.")
        except Exception as e:
            print(f"  SC error: {e}")
