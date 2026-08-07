import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

saavn_hosts = [
    "https://saavn-api-murex.vercel.app/api/search/songs?query=",
    "https://jiosaavn-api-v3.vercel.app/api/search/songs?query=",
    "https://jiosaavn-api.vercel.app/api/search/songs?query=",
    "https://saavn.dev/api/search/songs?query=",
    "https://saavn-api.vercel.app/search?query="
]

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu"]

for q in queries:
    print(f"\nQuery: {q}")
    for h in saavn_hosts:
        url = h + urllib.parse.quote(q)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    results = data.get('data', {}).get('results', []) or data.get('results', [])
                    if results:
                        song = results[0]
                        dl = song.get('downloadUrl', [])
                        print(f"  FOUND [{h[:35]}]: {song.get('name')} | DownloadUrls: {len(dl)}")
                        if dl:
                            print(f"    -> High quality MP3 URL: {dl[-1].get('url')}")
                        break
        except Exception as e:
            print(f"  Err [{h[:35]}]: {e}")
