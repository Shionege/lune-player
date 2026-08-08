import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test fetching YouTube playerResponse via android / tv embedded client with visitorData
official_videos = [
    ("Coldplay - Yellow", "yKNxeF4KMsY"),
    ("Ed Sheeran - Photograph", "KKQl-pIRQMY"),
    ("Erie Suzan - Senandung Rindu", "LWuL8rXkzJQ"),
    ("Denny Caknan - Crito Mustahil", "30BilwJ6bUw"),
    ("Sheila on 7 - Dan", "IWvo2fld3s4")
]

for title, vid in official_videos:
    print(f"\n================ Target Official Track: '{title}' (Vid: {vid}) ================")
    
    # Test POST https://www.youtube.com/youtubei/v1/player with TVHTML5_SIMPLY_EMBEDDED_PLAYER or ANDROID_TESTSUITE
    url = "https://www.youtube.com/youtubei/v1/player"
    payload = {
        "videoId": vid,
        "context": {
            "client": {
                "clientName": "TVHTML5_SIMPLY_EMBEDDED_PLAYER",
                "clientVersion": "2.0",
                "hl": "en",
                "gl": "US"
            }
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            streaming = data.get('streamingData', {})
            formats = streaming.get('adaptiveFormats', [])
            audio_formats = [f for f in formats if f.get('mimeType', '').startswith('audio/')]
            print(f"  TVHTML5_EMBED -> Found {len(audio_formats)} audio formats!")
            for af in audio_formats[:2]:
                url_val = af.get('url')
                clen = af.get('contentLength')
                mime = af.get('mimeType')
                if url_val:
                    print(f"  ✅ [DIRECT UN-CIPHERED 100% ORIGINAL AUDIO STREAM FOUND!]")
                    print(f"     Mime: {mime[:25]} | Length: {clen} bytes")
                    print(f"     Direct Link: {url_val[:100]}...")
                    
                    # Test HEAD request on direct link to verify status 200
                    hreq = urllib.request.Request(url_val, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
                    with urllib.request.urlopen(hreq, timeout=4, context=ctx) as hres:
                        print(f"     HTTP Status: {hres.status} | Content-Length: {hres.headers.get('Content-Length')}")
                    break
                else:
                    print(f"     Url missing for {mime[:25]}")
    except Exception as e:
        print(f"  Error: {e}")
