import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test resolving official YouTube video audio streams via public working CORS proxies / YTDL workers
official_videos = [
    ("Coldplay - Yellow (Official Video)", "yKNxeF4KMsY"),
    ("Ed Sheeran - Photograph (Official Video)", "KKQl-pIRQMY"),
    ("Erie Suzan - Senandung Rindu (Official Video)", "LWuL8rXkzJQ"),
    ("Denny Caknan - Crito Mustahil (Official Video)", "30BilwJ6bUw"),
    ("Sheila on 7 - Dan (Official Audio)", "IWvo2fld3s4")
]

resolvers = [
    "https://ytdl.cloud-357.workers.dev/?id=",
    "https://cobalt-api.kwiatekmom.tokyo",
    "https://api.cobalt.tools",
    "https://pipe.my-card.io/api/v1/videos/",
    "https://invidious.io"
]

for title, vid in official_videos:
    print(f"\n================ Official Track: '{title}' (ID: {vid}) ================")
    yt_url = f"https://www.youtube.com/watch?v={vid}"
    
    # Method 1: Test YouTube HTML playerResponse deciphering or stream URL extraction
    try:
        req = urllib.request.Request(yt_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            html = res.read().decode('utf-8')
            m = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});var', html) or re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});</script>', html)
            if m:
                pdata = json.loads(m.group(1))
                formats = pdata.get('streamingData', {}).get('adaptiveFormats', [])
                audio_formats = [f for f in formats if f.get('mimeType', '').startswith('audio/')]
                print(f"  YouTube HTML -> Found {len(audio_formats)} audio formats!")
                for af in audio_formats[:2]:
                    mime = af.get('mimeType')
                    bitrate = af.get('bitrate')
                    clen = af.get('contentLength')
                    url_val = af.get('url')
                    cipher_val = af.get('signatureCipher') or af.get('cipher')
                    print(f"    -> Mime: {mime[:25]} | Bitrate: {bitrate} | Length: {clen} bytes | URL: {bool(url_val)} | Cipher: {bool(cipher_val)}")
    except Exception as e:
        print(f"  YT HTML Error: {e}")
