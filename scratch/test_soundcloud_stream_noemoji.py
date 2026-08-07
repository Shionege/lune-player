import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

client_id = "iZ0W8VaxAfKmBTGbvB2TAYCi2znPfXBE"

queries = ["Ed Sheeran Photograph", "Coldplay Yellow", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir"]

for q in queries:
    print(f"\n================ SoundCloud API Search: '{q}' ================")
    sc_api = f"https://api-v2.soundcloud.com/search/tracks?q={urllib.parse.quote(q)}&client_id={client_id}&limit=10"
    try:
        req = urllib.request.Request(sc_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            collection = data.get('collection', [])
            print(f"  Total tracks found: {len(collection)}")
            for track in collection:
                duration = round(track.get('duration', 0) / 1000)
                # Filter tracks that are full length (> 120 seconds)
                if duration > 120:
                    title = track.get('title')
                    user = track.get('user', {}).get('username')
                    media = track.get('media', {}).get('transcodings', [])
                    print(f"  [FULL TRACK MATCH] Title: '{title}' by {user} | Duration: {duration}s ({round(duration/60,1)} min)")
                    
                    prog_mp3 = [m for m in media if m.get('format', {}).get('protocol') == 'progressive']
                    if prog_mp3:
                        stream_api = prog_mp3[0].get('url') + f"?client_id={client_id}"
                        sreq = urllib.request.Request(stream_api, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(sreq, timeout=5, context=ctx) as sres:
                            sdata = json.loads(sres.read().decode('utf-8'))
                            final_mp3_url = sdata.get('url')
                            print(f"     Direct Stream MP3 URL: {final_mp3_url[:100]}...")
                            hreq = urllib.request.Request(final_mp3_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(hreq, timeout=5, context=ctx) as hres:
                                print(f"     HTTP Status: {hres.status} | Content-Length: {hres.headers.get('Content-Length')} bytes")
                            break
    except Exception as e:
        print(f"  SC API Error: {e}")
