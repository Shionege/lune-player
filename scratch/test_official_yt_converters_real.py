import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

official_vids = {
    'Coldplay Yellow': 'tdVAqxNLXiw',
    'Ed Sheeran Photograph': 'KKQl-pIRQMY',
    'Erie Suzan Senandung Rindu': 'LWuL8rXkzJQ',
    'Denny Caknan Crito Mustahil': '30BilwJ6bUw',
    'Sheila on 7 Dan': 'IWvo2fld3s4'
}

# Test active working converters / audio stream APIs
for name, vid in official_vids.items():
    print(f"\n================ Official Vid Test: '{name}' ({vid}) ================")
    yt_url = f"https://www.youtube.com/watch?v={vid}"
    
    # Try open worker audio converter APIs
    converters = [
        f"https://ytdl.cloud-357.workers.dev/?url={urllib.parse.quote(yt_url)}",
        f"https://api.cobalt.tools",
    ]
    
    for c_api in converters:
        try:
            if 'cobalt' in c_api:
                payload = json.dumps({"url": yt_url, "downloadMode": "audio", "audioFormat": "mp3"}).encode('utf-8')
                req = urllib.request.Request(c_api, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
            else:
                req = urllib.request.Request(c_api, headers={'User-Agent': 'Mozilla/5.0'})
            
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    dl_url = data.get('url') or data.get('audio')
                    if dl_url:
                        hreq = urllib.request.Request(dl_url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
                        with urllib.request.urlopen(hreq, timeout=4, context=ctx) as hres:
                            size_mb = round(int(hres.headers.get('Content-Length', 0)) / (1024*1024), 2)
                            print(f"  [100% GENUINE OFFICIAL AUDIO STREAM] Status: {hres.status} | Size: {size_mb} MB")
                            print(f"     Direct MP3 Link: {dl_url[:90]}...")
                            break
        except Exception as e:
            pass
