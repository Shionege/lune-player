import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.youtube.com/watch?v=XMvKTY_0Eks"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
    html = res.read().decode('utf-8')
    key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
    if key_match:
        api_key = key_match.group(1)
        print(f"FOUND INNERTUBE_API_KEY: {api_key}")
        
        # Now test POST youtubei/v1/player with key
        player_api_url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"
        
        payloads = {
            "ANDROID": {
                "videoId": "XMvKTY_0Eks",
                "context": {
                    "client": {
                        "clientName": "ANDROID",
                        "clientVersion": "19.05.36",
                        "androidSdkVersion": 30
                    }
                }
            },
            "TVHTML5": {
                "videoId": "XMvKTY_0Eks",
                "context": {
                    "client": {
                        "clientName": "TVHTML5",
                        "clientVersion": "7.20230405.08.01"
                    }
                }
            },
            "WEB_EMBED": {
                "videoId": "XMvKTY_0Eks",
                "context": {
                    "client": {
                        "clientName": "WEB_EMBEDDED_PLAYER",
                        "clientVersion": "1.20230602.01.00"
                    }
                }
            }
        }
        
        for name, p in payloads.items():
            preq = urllib.request.Request(
                player_api_url,
                data=json.dumps(p).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            try:
                with urllib.request.urlopen(preq, timeout=5, context=ctx) as pres:
                    pdata = json.loads(pres.read().decode('utf-8'))
                    formats = pdata.get('streamingData', {}).get('adaptiveFormats', [])
                    audio_formats = [f for f in formats if f.get('mimeType', '').startswith('audio/')]
                    print(f"  Client {name} -> Found {len(audio_formats)} audio formats!")
                    for af in audio_formats[:2]:
                        u = af.get('url')
                        print(f"    -> Mime: {af.get('mimeType')[:20]} | URL present: {bool(u)}")
                        if u:
                            print(f"       DIRECT AUDIO STREAM URL: {u[:100]}...")
            except Exception as pe:
                print(f"  Client {name} -> Error: {pe}")
