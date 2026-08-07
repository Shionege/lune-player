import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://api.invidious.io/instances.json"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
    data = json.loads(res.read().decode('utf-8'))
    print("Total instances:", len(data))
    healthy = []
    for item in data:
        domain = item[0]
        info = item[1]
        if info.get('type') == 'https' and info.get('cors') and info.get('api'):
            uri = info.get('uri')
            healthy.append(uri)
    print("CORS HTTPS instances:", len(healthy))
    
    # Test top 5 instances for song 'Coldplay Yellow'
    vids = ['tdVAqxNLXiw', 'XMvKTY_0Eks']
    for uri in healthy[:10]:
        print(f"\nTesting Invidious instance: {uri}")
        for vid in vids:
            try:
                vurl = f"{uri}/api/v1/videos/{vid}"
                vreq = urllib.request.Request(vurl, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(vreq, timeout=4, context=ctx) as vres:
                    vdata = json.loads(vres.read().decode('utf-8'))
                    adaptive = vdata.get('adaptiveFormats', [])
                    audio_streams = [f for f in adaptive if f.get('type', '').startswith('audio/')]
                    if audio_streams:
                        print(f"  ✅ [SUCCESS] {uri} -> Video: {vid} | Audio stream count: {len(audio_streams)}")
                        print(f"     Direct MP3/M4A/WEBM URL: {audio_streams[0].get('url')[:100]}...")
                        break
            except Exception as e:
                print(f"  ❌ {uri} -> {e}")
