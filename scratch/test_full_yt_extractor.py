import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir"]

for q in queries:
    print(f"\n================ Target query: '{q}' ================")
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
                
                # Fetch video info from YouTube embed API (www.youtube.com/get_video_info or innertube embedded player)
                # Let's test calling youtube.com/youtubei/v1/player with WEB_CREATOR or TVHTML5_SIMPLY_EMBEDDED_PLAYER
                embed_url = "https://www.youtube.com/youtubei/v1/player"
                payload = {
                    "videoId": vid,
                    "context": {
                        "client": {
                            "clientName": "WEB_EMBEDDED_PLAYER",
                            "clientVersion": "1.20240801.01.00"
                        }
                    }
                }
                ereq = urllib.request.Request(
                    embed_url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(ereq, timeout=5, context=ctx) as eres:
                    edata = json.loads(eres.read().decode('utf-8'))
                    formats = edata.get('streamingData', {}).get('adaptiveFormats', [])
                    print(f"  WEB_EMBED formats count: {len(formats)}")
                    for f in formats:
                        if f.get('mimeType', '').startswith('audio/'):
                            print(f"    -> Mime: {f.get('mimeType')[:25]} | URL present: {bool(f.get('url'))} | Cipher: {bool(f.get('signatureCipher'))}")
    except Exception as e:
        print(f"  Search error: {e}")
