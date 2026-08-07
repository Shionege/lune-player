import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir", "Coldplay Yellow", "Ed Sheeran Photograph"]

piped_instances = [
    "https://pipedapi.kavin.rocks",
    "https://api.piped.privacydev.net",
    "https://pipedapi.col2.dev",
    "https://api.vibe.sh"
]

for q in queries:
    print(f"\n================ QUERY: {q} ================")
    for inst in piped_instances:
        url = f"{inst}/search?q={urllib.parse.quote(q)}&filter=music"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    items = data.get('items', [])
                    if items:
                        v_id = items[0].get('url', '').replace('/watch?v=', '')
                        title = items[0].get('title')
                        print(f"  SUCCESS [{inst[:30]}]: Title: {title} | Vid: {v_id}")
                        
                        # Now test fetching audio stream from stream endpoint
                        stream_url = f"{inst}/streams/{v_id}"
                        sreq = urllib.request.Request(stream_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(sreq, timeout=5, context=ctx) as sres:
                            sdata = json.loads(sres.read().decode('utf-8'))
                            audio_streams = sdata.get('audioStreams', [])
                            if audio_streams:
                                print(f"    -> AudioStream URL found! ({len(audioStreams)} streams) Mime: {audio_streams[0].get('mimeType')}")
                                print(f"    -> Stream Direct Link: {audio_streams[0].get('url')[:80]}...")
                                break
        except Exception as e:
            print(f"  FAIL [{inst[:30]}]: {e}")
