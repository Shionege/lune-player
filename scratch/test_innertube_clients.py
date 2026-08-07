import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

api_key = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
player_api_url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"

payloads = {
    "ANDROID_VR": {
        "videoId": "XMvKTY_0Eks",
        "context": {
            "client": {
                "clientName": "ANDROID_VR",
                "clientVersion": "1.56.2",
                "deviceModel": "Oculus Quest 2"
            }
        }
    },
    "ANDROID_MUSIC": {
        "videoId": "XMvKTY_0Eks",
        "context": {
            "client": {
                "clientName": "ANDROID_MUSIC",
                "clientVersion": "6.42.52",
                "androidSdkVersion": 31
            }
        }
    },
    "WEB": {
        "videoId": "XMvKTY_0Eks",
        "context": {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20240801.01.00"
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
            print(f"Client {name} -> Found {len(audio_formats)} audio formats!")
            for af in audio_formats[:3]:
                u = af.get('url')
                clen = af.get('contentLength')
                print(f"  -> Mime: {af.get('mimeType')[:30]} | Length: {clen} bytes | URL present: {bool(u)}")
                if u:
                    print(f"     ✅ DIRECT AUDIO URL: {u[:120]}...")
    except Exception as pe:
        print(f"Client {name} -> Error: {pe}")
