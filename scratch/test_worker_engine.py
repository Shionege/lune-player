import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

cid = "TwElDfIgW9RpAzLMUSy9g1VvI2Kao7my"
queries = ["Ed Sheeran Photograph", "Coldplay Yellow", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir", "Coldplay Viva La Vida"]

for cleanQ in queries:
    print(f"\nWorker Stream Engine Test: '{cleanQ}'")
    scApi = f"https://api-v2.soundcloud.com/search/tracks?q={urllib.parse.quote(cleanQ)}&client_id={cid}&limit=10"
    try:
        req = urllib.request.Request(scApi, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            tracks = data.get('collection', [])
            success = False
            for tr in tracks:
                dur = tr.get('duration', 0)
                if dur > 100000:
                    media = tr.get('media', {}).get('transcodings', [])
                    prog = [m for m in media if m.get('format', {}).get('protocol') == 'progressive']
                    if prog:
                        stream_api = prog[0].get('url') + f"?client_id={cid}"
                        sreq = urllib.request.Request(stream_api, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(sreq, timeout=5, context=ctx) as sres:
                            sdata = json.loads(sres.read().decode('utf-8'))
                            final_url = sdata.get('url')
                            if final_url:
                                hreq = urllib.request.Request(final_url, headers={'User-Agent': 'Mozilla/5.0'})
                                with urllib.request.urlopen(hreq, timeout=5, context=ctx) as hres:
                                    size_mb = round(int(hres.headers.get('Content-Length', 0)) / (1024*1024), 2)
                                    print(f"  ✅ [100% FULL SONG SUCCESS] Title: '{tr.get('title')}'")
                                    print(f"     Duration: {round(dur/1000)}s | File Size: {size_mb} MB | Status: {hres.status}")
                                    success = True
                                    break
            if not success:
                print("  ❌ SoundCloud full track not found, falling back to Archive...")
    except Exception as e:
        print(f"  Error: {e}")
