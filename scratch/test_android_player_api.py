import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

vids = ['tdVAqxNLXiw', 'KKQl-pIRQMY', 'XMvKTY_0Eks', 'jhAHUF_40zk']

for vid in vids:
    print(f"\n================ Target Video ID: {vid} ================")
    url = "https://www.youtube.com/youtubei/v1/player"
    
    payload = {
        "videoId": vid,
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "19.05.36",
                "androidSdkVersion": 30,
                "hl": "en",
                "gl": "US"
            }
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'com.google.android.youtube/19.05.36 (Linux; U; Android 11)'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            streaming = data.get('streamingData', {})
            formats = streaming.get('adaptiveFormats', [])
            audio_formats = [f for f in formats if f.get('mimeType', '').startswith('audio/')]
            print(f"  Android Client API -> Found {len(audio_formats)} audio formats!")
            for af in audio_formats[:2]:
                direct_url = af.get('url')
                content_len = af.get('contentLength', 'unknown')
                bitrate = af.get('bitrate')
                mime = af.get('mimeType')
                if direct_url:
                    print(f"  ✅ [DIRECT MP4/WEBM AUDIO STREAM FOUND!]")
                    print(f"     Mime: {mime} | Length: {content_len} bytes | Bitrate: {bitrate}")
                    print(f"     Direct URL: {direct_url[:100]}...")
                else:
                    print(f"     URL missing for {mime}")
    except Exception as e:
        print(f"  Error: {e}")
