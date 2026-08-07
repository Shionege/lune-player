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
    instances = [item[1].get('uri') for item in data if item[1].get('type') == 'https' and item[1].get('uri')]
    print("All HTTPS Invidious instances:", len(instances))
    
    vids = ['XMvKTY_0Eks', 'tdVAqxNLXiw']
    for uri in instances:
        for vid in vids:
            try:
                vurl = f"{uri}/api/v1/videos/{vid}"
                vreq = urllib.request.Request(vurl, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(vreq, timeout=4, context=ctx) as vres:
                    if vres.status == 200:
                        vdata = json.loads(vres.read().decode('utf-8'))
                        adaptive = vdata.get('adaptiveFormats', [])
                        audio_streams = [f for f in adaptive if f.get('type', '').startswith('audio/')]
                        if audio_streams:
                            print(f"SUCCESS [{uri}]: Video {vid} -> Audio stream URL: {audio_streams[0].get('url')[:80]}...")
                            break
            except Exception as e:
                print(f"FAIL [{uri}]: {e}")
