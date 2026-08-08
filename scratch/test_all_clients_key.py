import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.youtube.com/watch?v=yKNxeF4KMsY"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
    html = res.read().decode('utf-8')
    key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
    api_key = key_match.group(1) if key_match else "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"

player_api_url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"

clients = [
    ("ANDROID_TESTSUITE", "1.9.0"),
    ("ANDROID_VR", "1.56.2"),
    ("WEB_EMBEDDED_PLAYER", "1.20240801.01.00"),
    ("TVHTML5", "7.20230405.08.01"),
    ("IOS", "19.29.1")
]

vid = "yKNxeF4KMsY" # Coldplay Yellow Official Video

for cname, cver in clients:
    payload = {
        "videoId": vid,
        "context": {
            "client": {
                "clientName": cname,
                "clientVersion": cver
            }
        }
    }
    preq = urllib.request.Request(
        player_api_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(preq, timeout=4, context=ctx) as pres:
            pdata = json.loads(pres.read().decode('utf-8'))
            formats = pdata.get('streamingData', {}).get('adaptiveFormats', [])
            audio_formats = [f for f in formats if f.get('mimeType', '').startswith('audio/')]
            print(f"Client {cname} -> Found {len(audio_formats)} audio formats!")
            for af in audio_formats[:2]:
                u = af.get('url')
                clen = af.get('contentLength')
                print(f"  -> Mime: {af.get('mimeType')[:25]} | Length: {clen} | URL: {bool(u)}")
                if u:
                    print(f"     ✅ DIRECT AUDIO URL: {u[:100]}...")
    except Exception as pe:
        print(f"Client {cname} -> Error: {pe}")
