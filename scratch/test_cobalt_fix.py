import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

vids = ['WJ9F2qiw3wg', 'C8l-A7HxXmY', '2P4WT0b0myo', '6sKRBRSUego']

cobalt_instances = [
    "https://api.cobalt.tools",
    "https://co.wuk.sh"
]

for v in vids:
    print(f"\nTesting YouTube Video ID: {v}")
    yt_url = f"https://www.youtube.com/watch?v={v}"
    for inst in cobalt_instances:
        try:
            req = urllib.request.Request(
                inst,
                data=json.dumps({"url": yt_url, "downloadMode": "audio", "audioFormat": "mp3"}).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                }
            )
            with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    print(f"  SUCCESS: {inst} -> Status: {data.get('status')}, URL: {str(data.get('url'))[:60]}")
                    break
        except Exception as e:
            print(f"  FAIL: {inst} -> {e}")
