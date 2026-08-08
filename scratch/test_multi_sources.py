import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cid = "TwElDfIgW9RpAzLMUSy9g1VvI2Kao7my"
queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil"]

for q in queries:
    print(f"\n================ Fetching Multiple Audio Sources for: '{q}' ================")
    sources = []
    
    # Provider 1: SoundCloud Search
    sc_api = f"https://api-v2.soundcloud.com/search/tracks?q={urllib.parse.quote(q)}&client_id={cid}&limit=10"
    try:
        req = urllib.request.Request(sc_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            collection = data.get('collection', [])
            for tr in collection:
                dur = round(tr.get('duration', 0) / 1000)
                if dur > 100:
                    title = tr.get('title')
                    uploader = tr.get('user', {}).get('username')
                    media = tr.get('media', {}).get('transcodings', [])
                    prog = [m for m in media if m.get('format', {}).get('protocol') == 'progressive']
                    if prog:
                        sources.append({
                            'id': f"sc_{tr.get('id')}",
                            'provider': 'SoundCloud',
                            'title': title,
                            'uploader': uploader,
                            'duration': f"{dur//60}:{dur%60:02d}",
                            'transcoding_url': prog[0].get('url')
                        })
    except Exception as e:
        print(f"  SC error: {e}")
        
    # Provider 2: Archive.org Search
    a_api = f"https://archive.org/advancedsearch.php?q=%28{urllib.parse.quote(q)}%29+AND+mediatype%3A%28audio%29&fl[]=identifier,title,creator,duration&rows=5&output=json"
    try:
        req = urllib.request.Request(a_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            docs = data.get('response', {}).get('docs', [])
            for d in docs:
                sources.append({
                    'id': f"archive_{d.get('identifier')}",
                    'provider': 'Archive.org',
                    'title': d.get('title'),
                    'uploader': d.get('creator') or 'Archive',
                    'duration': d.get('duration', 'N/A'),
                    'transcoding_url': f"https://archive.org/metadata/{d.get('identifier')}"
                })
    except Exception as e:
        print(f"  Archive error: {e}")
        
    print(f"  Total distinct audio sources found: {len(sources)}")
    for idx, s in enumerate(sources[:6], 1):
        print(f"  [{idx}] [{s['provider']}] Title: '{s['title']}' | Uploader: '{s['uploader']}' | Dur: {s['duration']}")
