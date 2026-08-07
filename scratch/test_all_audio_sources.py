import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir"]

test_apis = [
    # JioSaavn API variants
    "https://saavn.dev/api/search/songs?query=",
    "https://saavn.me/api/search/songs?query=",
    "https://jiosaavn-api.vercel.app/search?query=",
    "https://jio-saavn-api.vercel.app/search?query=",
    "https://saavn-api-murex.vercel.app/search?query=",
    "https://jiosaavn-api-v3.vercel.app/search?query=",
    # Audiomack
    "https://api.audiomack.com/v1/search?q=",
    # Deezer
    "https://api.deezer.com/search?q="
]

for q in queries:
    print(f"\n=================== QUERY: {q} ===================")
    for api in test_apis:
        url = api + urllib.parse.quote(q)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    print(f"✅ [SUCCESS] {api[:40]} -> {str(data)[:150]}")
        except Exception as e:
            print(f"❌ [FAIL] {api[:40]} -> {e}")
