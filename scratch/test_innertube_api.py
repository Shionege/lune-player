import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test YouTube InnerTube API (ANDROID / WEB client)
test_video_ids = [
    "yKNxeF4KMsY", # Coldplay Yellow
    "SPKBtUPA92E", # Denny Caknan Crito Mustahil
    "nSDgHBxUbVQ", # Ed Sheeran Photograph
]

clients = [
    {"clientName": "ANDROID", "clientVersion": "19.02.34"},
    {"clientName": "WEB", "clientVersion": "2.20240101.00.00"},
    {"clientName": "IOS", "clientVersion": "19.02.1", "deviceModel": "iPhone14,3"}
]

for vid in test_video_ids:
    print(f"\n================ Testing InnerTube API for Video ID: {vid} ================")
    for c in clients:
        try:
            url = "https://www.youtube.com/youtubei/v1/player"
            payload = json.dumps({
                "videoId": vid,
                "context": {
                    "client": c
                }
            }).encode('utf-8')
            
            req = urllib.request.Request(url, data=payload, headers={
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/json'
            })
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    streamingData = data.get('streamingData', {})
                    adaptive = streamingData.get('adaptiveFormats', [])
                    audio_formats = [f for f in adaptive if 'audio' in f.get('mimeType', '')]
                    print(f"  [Client: {c.get('clientName')}] Status: {data.get('playabilityStatus', {}).get('status')} | Found {len(audio_formats)} audio streams!")
                    for af in audio_formats[:2]:
                        bitrate = af.get('bitrate')
                        mime = af.get('mimeType')
                        stream_url = af.get('url')
                        if stream_url:
                            print(f"    ✅ DIRECT AUDIO STREAM FOUND! Bitrate: {bitrate}, Mime: {mime}")
                            print(f"       Stream URL: {stream_url[:80]}...")
                        elif af.get('signatureCipher') or af.get('cipher'):
                            print(f"    ℹ️ Cipher protected stream found (bitrate: {bitrate})")
                    if audio_formats:
                        break
        except Exception as e:
            print(f"  Failed client {c.get('clientName')}: {e}")
