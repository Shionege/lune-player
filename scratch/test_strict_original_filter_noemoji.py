import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cid = "TwElDfIgW9RpAzLMUSy9g1VvI2Kao7my"

queries = [
    ("Coldplay", "Yellow", 269),
    ("Ed Sheeran", "Photograph", 259),
    ("Ariana Grande", "hate that i made you love me", 199),
    ("Erie Suzan", "Senandung Rindu", 269),
    ("Denny Caknan", "Crito Mustahil", 287)
]

for artist, title, target_dur in queries:
    print(f"\n================ Target: '{artist} - {title}' (Target Dur: {target_dur}s) ================")
    sc_api = f"https://api-v2.soundcloud.com/search/tracks?q={urllib.parse.quote(artist + ' ' + title)}&client_id={cid}&limit=15"
    try:
        req = urllib.request.Request(sc_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            collection = data.get('collection', [])
            
            banned_keywords = ['cover', 'remix', 'slowed', 'reverb', 'karaoke', 'instrumental', 'acoustic', '8d', 'nightcore', 'speed up']
            
            original_candidates = []
            for track in collection:
                t_title = track.get('title', '').lower()
                dur = round(track.get('duration', 0) / 1000)
                user = track.get('user', {}).get('username')
                
                is_banned = any(b in t_title for b in banned_keywords)
                if not is_banned and dur > 100:
                    diff = abs(dur - target_dur)
                    original_candidates.append((diff, track))
            
            original_candidates.sort(key=lambda x: x[0])
            
            if original_candidates:
                best_track = original_candidates[0][1]
                b_dur = round(best_track.get('duration', 0) / 1000)
                print(f"  [100% ORIGINAL STUDIO TRACK MATCH] Title: '{best_track.get('title')}' by {best_track.get('user', {}).get('username')} ({b_dur}s)")
            else:
                print("  No candidate passed strict original filter!")
    except Exception as e:
        print(f"  Error: {e}")
