import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

piped_apis = [
    "https://pipedapi.kavin.rocks",
    "https://piped-api.garudalinux.org",
    "https://api.piped.video",
    "https://pipedapi.tokhmi.xyz",
    "https://pipedapi.moomoo.me",
    "https://pipedapi.syncflix.org",
    "https://pipedapi.adminforge.de",
    "https://pipedapi.in.projectsegfau.lt",
    "https://pipedapi.rivet.gg"
]

vids = ['tdVAqxNLXiw', 'XMvKTY_0Eks']

for api in piped_apis:
    print(f"\nTesting Piped instance: {api}")
    for vid in vids:
        url = f"{api}/streams/{vid}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    audio_streams = data.get('audioStreams', [])
                    if audio_streams:
                        print(f"  [SUCCESS] {api} -> Vid: {vid}")
                        print(f"     Direct Link: {audio_streams[0].get('url')[:90]}...")
                        print(f"     MimeType: {audio_streams[0].get('mimeType')} | Bitrate: {audio_streams[0].get('bitrate')}")
                        break
        except Exception as e:
            print(f"  [FAIL] {api} -> {e}")
