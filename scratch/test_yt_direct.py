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
    yt_search = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q + ' audio')}"
    req = urllib.request.Request(yt_search, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            html = res.read().decode('utf-8')
            vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            if vids:
                vid = vids[0]
                print(f"  Found YouTube Video ID: {vid}")
                
                # Test fetching YouTube embed / watch page playerResponse directly
                player_url = f"https://www.youtube.com/watch?v={vid}"
                preq = urllib.request.Request(player_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(preq, timeout=5, context=ctx) as pres:
                    phtml = pres.read().decode('utf-8')
                    # Look for ytInitialPlayerResponse
                    m = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});var', phtml) or re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});</script>', phtml)
                    if m:
                        pdata = json.loads(m.group(1))
                        formats = pdata.get('streamingData', {}).get('adaptiveFormats', [])
                        audio_formats = [f for f in formats if f.get('mimeType', '').startswith('audio/')]
                        print(f"  SUCCESS: Found {len(audio_formats)} audio formats directly from YouTube!")
                        for af in audio_formats[:2]:
                            print(f"    -> Mime: {af.get('mimeType')} | Bitrate: {af.get('bitrate')} | URL len: {len(af.get('url', ''))}")
    except Exception as e:
        print(f"  Search fail: {e}")
