import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir", "Ed Sheeran Photograph", "Coldplay Yellow", "Denny Caknan"]

endpoints = [
    "https://saavn.me/search/songs?query=",
    "https://saavn.dev/api/search/songs?query=",
    "https://jiosaavn-api-v3.vercel.app/search?query=",
    "https://jiosaavn-api.vercel.app/search?query="
]

for q in queries:
    print(f"\n================ QUERY: {q} ================")
    for ep in endpoints:
        url = ep + urllib.parse.quote(q)
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json'
            })
            with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
                if res.status == 200:
                    raw = res.read().decode('utf-8')
                    try:
                        data = json.loads(raw)
                        res_list = data.get('data', {}).get('results', []) or data.get('results', [])
                        if res_list:
                            s = res_list[0]
                            title = s.get('name') or s.get('title')
                            durl = s.get('downloadUrl') or s.get('media_url')
                            print(f"  SUCCESS [{ep[:30]}]: {title} -> Stream: {durl}")
                            break
                        else:
                            print(f"  EMPTY RESULTS [{ep[:30]}]")
                    except Exception as je:
                        print(f"  NON-JSON [{ep[:30]}]: len {len(raw)}")
        except Exception as e:
            print(f"  FAIL [{ep[:30]}]: {e}")
