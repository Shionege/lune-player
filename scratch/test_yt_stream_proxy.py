import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir"]

for q in queries:
    print(f"\nTarget query: '{q}'")
    # Step 1: Search YouTube for Video ID
    yt_search = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q + ' audio')}"
    req = urllib.request.Request(yt_search, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            html = res.read().decode('utf-8')
            vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if vids:
                vid = vids[0]
                print(f"  Found YouTube Video ID: {vid}")
                
                # Step 2: Fetch stream URL via Invidious / Piped APIs
                invidious_apis = [
                    f"https://inv.zoomerville.com/api/v1/videos/{vid}",
                    f"https://invidious.nerdvpn.de/api/v1/videos/{vid}",
                    f"https://api.piped.video/streams/{vid}"
                ]
                for api in invidious_apis:
                    try:
                        areq = urllib.request.Request(api, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(areq, timeout=4, context=ctx) as ares:
                            adata = json.loads(ares.read().decode('utf-8'))
                            adaptive = adata.get('adaptiveFormats', []) or adata.get('audioStreams', [])
                            audio_urls = [f.get('url') for f in adaptive if 'audio' in f.get('type', '') or 'audio' in f.get('mimeType', '')]
                            if audio_urls:
                                print(f"  ✅ [FULL STREAM SUCCESS] API: {api[:35]}... | Audio Stream URL: {audio_urls[0][:80]}...")
                                break
                    except Exception as ae:
                        print(f"  ❌ API Fail: {api[:35]} -> {ae}")
    except Exception as e:
        print(f"  Search fail: {e}")
