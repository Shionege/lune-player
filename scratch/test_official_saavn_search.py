import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test saavn.dev and other public Saavn API deployments
endpoints = [
    "https://saavn.dev/api/search/songs?query=",
    "https://jiosaavn-api-v3.vercel.app/search?query=",
    "https://saavn-api.vercel.app/search?query="
]

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Ariana Grande", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil", "Sheila on 7 Dan"]

for q in queries:
    print(f"\n================ Official Query: '{q}' ================")
    for ep in endpoints:
        url = ep + urllib.parse.quote(q)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    raw = res.read().decode('utf-8')
                    try:
                        data = json.loads(raw)
                        results = data.get('data', {}).get('results', []) or data.get('results', [])
                        if results:
                            print(f"  API [{ep[:30]}] returned {len(results)} songs!")
                            for s in results[:3]:
                                name = s.get('name') or s.get('title')
                                artist = s.get('primaryArtists') or s.get('singers') or s.get('artist')
                                album = s.get('album', {}).get('name') if isinstance(s.get('album'), dict) else s.get('album')
                                download_urls = s.get('downloadUrl', []) or s.get('media_url', '')
                                print(f"    -> Title: '{name}' | Artist: '{artist}' | Album: '{album}'")
                                if isinstance(download_urls, list) and download_urls:
                                    print(f"       HQ MP3 URL (320kbps): {download_urls[-1].get('url')[:90]}...")
                                elif isinstance(download_urls, str) and download_urls:
                                    print(f"       Direct Media URL: {download_urls[:90]}...")
                            break
                    except Exception as je:
                        pass
        except Exception as e:
            pass
