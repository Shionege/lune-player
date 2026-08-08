import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

official_vids = {
    'Coldplay Yellow': 'yKNxeF4KMsY',
    'Ed Sheeran Photograph': 'KKQl-pIRQMY',
    'Ariana Grande hate that i made you love me': '8dVWVqoVQxo',
    'Erie Suzan Senandung Rindu': 'LWuL8rXkzJQ',
    'Denny Caknan Crito Mustahil': '30BilwJ6bUw',
    'Sheila on 7 Dan': 'IWvo2fld3s4'
}

# Test active public converter APIs to resolve direct MP3 links for these official video IDs
converter_apis = [
    "https://api.cobalt.tools",
    "https://cobalt-api.kwiatekmom.tokyo",
    "https://ytdl.cloud-357.workers.dev/?url="
]

for name, vid in official_vids.items():
    print(f"\n================ Official Vid: '{name}' (ID: {vid}) ================")
    yt_url = f"https://www.youtube.com/watch?v={vid}"
    
    # Test cobalt-like JSON POST or worker GET
    for inst in ["https://api.cobalt.tools", "https://cobalt-api.kwiatekmom.tokyo"]:
        try:
            req = urllib.request.Request(
                inst,
                data=json.dumps({"url": yt_url, "downloadMode": "audio", "audioFormat": "mp3"}).encode('utf-8'),
                headers={'Content-Type': 'application/json', 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    dl_url = data.get('url')
                    if dl_url:
                        print(f"  ✅ [OFFICIAL ORIGINAL AUDIO RESOLVED] {inst[:30]} -> {dl_url[:90]}...")
                        break
        except Exception as e:
            pass
