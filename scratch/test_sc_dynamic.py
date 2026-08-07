import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get_sc_client_id():
    req = urllib.request.Request("https://soundcloud.com", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        html = res.read().decode('utf-8')
        js_urls = re.findall(r'src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"', html)
        for js in reversed(js_urls):
            jreq = urllib.request.Request(js, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urllib.request.urlopen(jreq, timeout=4, context=ctx) as jres:
                    jtext = jres.read().decode('utf-8')
                    cids = re.findall(r'client_id[:=]"([a-zA-Z0-9]{32})"', jtext)
                    if cids:
                        return cids[0]
            except Exception as e:
                pass
    return None

client_id = get_sc_client_id()
print(f"Dynamic SoundCloud client_id: {client_id}")

queries = ["Ed Sheeran Photograph", "Coldplay Yellow", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir"]

if client_id:
    for q in queries:
        print(f"\n================ SoundCloud Search: '{q}' ================")
        sc_api = f"https://api-v2.soundcloud.com/search/tracks?q={urllib.parse.quote(q)}&client_id={client_id}&limit=10"
        try:
            req = urllib.request.Request(sc_api, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
                data = json.loads(res.read().decode('utf-8'))
                collection = data.get('collection', [])
                for track in collection:
                    duration = round(track.get('duration', 0) / 1000)
                    if duration > 120:
                        title = track.get('title')
                        user = track.get('user', {}).get('username')
                        media = track.get('media', {}).get('transcodings', [])
                        prog_mp3 = [m for m in media if m.get('format', {}).get('protocol') == 'progressive']
                        if prog_mp3:
                            stream_api = prog_mp3[0].get('url') + f"?client_id={client_id}"
                            sreq = urllib.request.Request(stream_api, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(sreq, timeout=5, context=ctx) as sres:
                                sdata = json.loads(sres.read().decode('utf-8'))
                                final_mp3_url = sdata.get('url')
                                hreq = urllib.request.Request(final_mp3_url, headers={'User-Agent': 'Mozilla/5.0'})
                                with urllib.request.urlopen(hreq, timeout=5, context=ctx) as hres:
                                    print(f"  [SUCCESS FULL SONG] '{title}' by {user} ({duration}s)")
                                    print(f"     Status: {hres.status} | Content-Length: {hres.headers.get('Content-Length')} bytes")
                                    print(f"     MP3 Link: {final_mp3_url[:100]}...")
                                break
        except Exception as e:
            print(f"  Error: {e}")
