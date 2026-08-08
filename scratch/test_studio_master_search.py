import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cid = "TwElDfIgW9RpAzLMUSy9g1VvI2Kao7my"

queries = [
    ("Coldplay", "Yellow"),
    ("Ed Sheeran", "Photograph"),
    ("Ariana Grande", "hate that i made you love me"),
    ("Erie Suzan", "Senandung Rindu"),
    ("Denny Caknan", "Crito Mustahil"),
    ("Sheila on 7", "Dan")
]

for artist, title in queries:
    print(f"\n================ Strict Studio Master Search: '{artist} - {title}' ================")
    # Query SoundCloud for "artist title"
    q_str = f"{artist} {title}"
    sc_api = f"https://api-v2.soundcloud.com/search/tracks?q={urllib.parse.quote(q_str)}&client_id={cid}&limit=20"
    try:
        req = urllib.request.Request(sc_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            collection = data.get('collection', [])
            
            banned = ['cover', 'remix', 'slowed', 'reverb', 'karaoke', 'instrumental', 'acoustic', '8d', 'nightcore', 'speed up', 'sped up', 'tribute', 'mashup', 'edit', 'flip', 'bootleg']
            
            studio_masters = []
            for tr in collection:
                t_title = tr.get('title', '').lower()
                u_name = tr.get('user', {}).get('username', '').lower()
                dur = round(tr.get('duration', 0) / 1000)
                
                is_banned = any(b in t_title for b in banned)
                if not is_banned and dur > 120:
                    studio_masters.append(tr)
            
            print(f"  Strict Original Candidates found: {len(studio_masters)}")
            for sm in studio_masters[:3]:
                st_title = str(sm.get('title')).encode('ascii', 'ignore').decode('ascii')
                st_user = str(sm.get('user', {}).get('username')).encode('ascii', 'ignore').decode('ascii')
                dur = round(sm.get('duration', 0) / 1000)
                print(f"  -> [GENUINE STUDIO RECORDING] Title: '{st_title}' | Uploader: '{st_user}' | Dur: {dur}s")
    except Exception as e:
        print(f"  Error: {e}")
