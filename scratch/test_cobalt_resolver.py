import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test Cobalt API instances and YouTube Music search resolvers
queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil"]

# Cobalt API instances
cobalt_instances = [
    "https://api.cobalt.tools/api/json",
    "https://cobalt.xy-27.dev/api/json",
    "https://co.wuk.sh/api/json",
    "https://cobalt-api.kwiatekmoms.com/api/json"
]

# YouTube search without API key via Invidious/Piped fallback
print("=== 3. TESTING COBALT API RESOLVER FOR YOUTUBE MUSIC ===")
test_yt_urls = [
    "https://www.youtube.com/watch?v=yKNxeF4KMsY", # Coldplay Yellow
    "https://www.youtube.com/watch?v=SPKBtUPA92E", # Denny Caknan Crito Mustahil
]

for yt_url in test_yt_urls:
    print(f"\nTarget YouTube URL: {yt_url}")
    for c_url in cobalt_instances:
        try:
            payload = json.dumps({"url": yt_url, "isAudioOnly": True, "aFormat": "mp3"}).encode('utf-8')
            req = urllib.request.Request(c_url, data=payload, headers={
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    print(f"  [{c_url}] SUCCESS! Status: {data.get('status')}")
                    if data.get('url'):
                        print(f"    ✅ Direct Audio Stream URL: {data.get('url')[:80]}...")
                        break
        except Exception as e:
            # print(f"  Failed {c_url}: {e}")
            pass
