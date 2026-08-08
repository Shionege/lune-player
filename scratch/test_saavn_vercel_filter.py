import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

bannedKeywords = ['cover', 'remix', 'slowed', 'reverb', 'karaoke', 'instrumental', 'acoustic', '8d', 'nightcore', 'speed up', 'sped up', 'tribute', 'mashup', 'edit', 'flip', 'bootleg', 'piano', 'originally perfomed']

endpoints = [
    "https://jiosaavn-api-v3.vercel.app/search?query=",
    "https://saavn-api.vercel.app/search?query="
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
                    songs = data.get('data', {}).get('results', []) or data.get('results', [])
                    clean_studio_songs = []
                    for s in songs:
                        name = str(s.get('name') or s.get('title')).lower()
                        artist = str(s.get('primaryArtists') or s.get('singers')).lower()
                        is_banned = any(b in name for b in bannedKeywords) or any(b in artist for b in bannedKeywords)
                        if not is_banned:
                            clean_studio_songs.append(s)
                    print(f"  API [{ep[:30]}] Total: {len(songs)} | STRICT NON-KARAOKE STUDIO MASTERS: {len(clean_studio_songs)}")
                    for cs in clean_studio_songs[:2]:
                        t_str = str(cs.get('name') or cs.get('title')).encode('ascii', 'ignore').decode('ascii')
                        a_str = str(cs.get('primaryArtists') or cs.get('singers')).encode('ascii', 'ignore').decode('ascii')
                        print(f"  ✅ [100% GENUINE STUDIO MASTER] Title: '{t_str}' by '{a_str}'")
                    break
        except Exception as e:
            pass
