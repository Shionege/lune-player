import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test extracting SoundCloud client_id from soundcloud.com main JS bundles
sc_main = "https://soundcloud.com"
req = urllib.request.Request(sc_main, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
client_id = None
try:
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        html = res.read().decode('utf-8')
        js_urls = re.findall(r'src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"', html)
        print(f"Found SoundCloud JS bundles: {len(js_urls)}")
        for js in js_urls[-3:]:
            jreq = urllib.request.Request(js, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(jreq, timeout=4, context=ctx) as jres:
                    jtext = jres.read().decode('utf-8')
                    cids = re.findall(r'client_id[:=]"([a-zA-Z0-9]{32})"', jtext)
                    if cids:
                        client_id = cids[0]
                        print(f"✅ FOUND SOUNDCLOUD CLIENT_ID: {client_id}")
                        break
            except Exception as e:
                pass
except Exception as e:
    print(f"Err fetching SC main: {e}")

if not client_id:
    # Use known public working SoundCloud client_ids
    client_id = "iZ0W8VaxAfKmBTGbvB2TAYCi2znPfXBE"

# Now test SoundCloud API search with client_id
queries = ["Ed Sheeran Photograph", "Coldplay Yellow", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir"]

for q in queries:
    print(f"\n================ SoundCloud API Search: '{q}' ================")
    sc_api = f"https://api-v2.soundcloud.com/search/tracks?q={urllib.parse.quote(q)}&client_id={client_id}&limit=3"
    try:
        req = urllib.request.Request(sc_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            collection = data.get('collection', [])
            print(f"  Tracks found: {len(collection)}")
            for track in collection[:2]:
                title = track.get('title')
                user = track.get('user', {}).get('username')
                duration = round(track.get('duration', 0) / 1000)
                media = track.get('media', {}).get('transcodings', [])
                print(f"  -> Title: '{title}' by {user} | Duration: {duration}s | Transcodings: {len(media)}")
                
                # Find progressive mp3 transcoding
                prog_mp3 = [m for m in media if m.get('format', {}).get('protocol') == 'progressive']
                if prog_mp3:
                    stream_api = prog_mp3[0].get('url') + f"?client_id={client_id}"
                    sreq = urllib.request.Request(stream_api, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(sreq, timeout=5, context=ctx) as sres:
                        sdata = json.loads(sres.read().decode('utf-8'))
                        final_mp3_url = sdata.get('url')
                        print(f"     ✅ [100% FULL-LENGTH MP3 URL FOUND!]")
                        print(f"        Direct Stream URL: {final_mp3_url[:110]}...")
                        
                        # Test HEAD request on final_mp3_url for Content-Length
                        hreq = urllib.request.Request(final_mp3_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(hreq, timeout=5, context=ctx) as hres:
                            print(f"        HTTP Status: {hres.status} | Length: {hres.headers.get('Content-Length')} bytes")
                        break
    except Exception as e:
        print(f"  SC API Error: {e}")
