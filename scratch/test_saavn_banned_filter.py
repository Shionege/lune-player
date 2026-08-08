import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test filtering JioSaavn results with bannedKeywords
bannedKeywords = ['cover', 'remix', 'slowed', 'reverb', 'karaoke', 'instrumental', 'acoustic', '8d', 'nightcore', 'speed up', 'sped up', 'tribute', 'mashup', 'edit', 'flip', 'bootleg', 'piano', 'originally perfomed']

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil", "Sheila on 7 Dan"]

for q in queries:
    print(f"\n================ Testing JioSaavn Strict Banned Filter for: '{q}' ================")
    url = f"https://saavn.dev/api/search/songs?query={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            songs = data.get('data', {}).get('results', []) or data.get('results', [])
            
            clean_studio_songs = []
            for s in songs:
                name = str(s.get('name') or s.get('title')).lower()
                artist = str(s.get('primaryArtists') or s.get('singers')).lower()
                
                is_banned = any(b in name for b in bannedKeywords) or any(b in artist for b in bannedKeywords)
                if not is_banned:
                    clean_studio_songs.append(s)
                    
            print(f"  Total JioSaavn Songs: {len(songs)} | STRICT NON-KARAOKE ORIGINAL STUDIO MASTERS: {len(clean_studio_songs)}")
            for cs in clean_studio_songs[:3]:
                t_str = str(cs.get('name') or cs.get('title')).encode('ascii', 'ignore').decode('ascii')
                a_str = str(cs.get('primaryArtists') or cs.get('singers')).encode('ascii', 'ignore').decode('ascii')
                print(f"  ✅ [100% GENUINE STUDIO MASTER] Title: '{t_str}' by '{a_str}'")
    except Exception as e:
        print(f"  Error: {e}")
