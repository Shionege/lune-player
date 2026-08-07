import urllib.request
import json

queries = ["Senandung Rindu Erie Suzan", "Photograph Ed Sheeran", "Yellow Coldplay", "Denny Caknan"]

apis = [
    "https://saavn.dev/api/search/songs?query=",
    "https://saavn.me/search/songs?query=",
    "https://jiosaavn-api-v3.vercel.app/search?query="
]

for q in queries:
    print(f"\n--- Searching query: '{q}' ---")
    for api in apis:
        url = api + urllib.parse.quote(q)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    results = data.get('data', {}).get('results', []) or data.get('results', [])
                    if results:
                        song = results[0]
                        download_urls = song.get('downloadUrl', []) or song.get('media_url', '')
                        print(f"  [SUCCESS] API: {api[:30]}... | Title: {song.get('name') or song.get('title')} | Stream: {download_urls}")
                        break
        except Exception as e:
            print(f"  [FAIL] API: {api[:30]}... -> {e}")
