import urllib.request
import json
import ssl
import sys

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test Saavn.dev and Deezer endpoints
queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil", "Sheila on 7 Dan"]

print("=== TESTING SAAVN & DEEZER STREAM ENGINE ===")

for q in queries:
    print(f"\n================ Query: '{q}' ================")
    
    # 1. Test Saavn 320k via Vercel mirror
    saavn_eps = [
        "https://jiosaavn-api-v3.vercel.app/search?query=",
        "https://saavn.dev/api/search/songs?query="
    ]
    for sep in saavn_eps:
        try:
            url = sep + urllib.parse.quote(q)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    songs = data.get('data', {}).get('results', []) or data.get('results', [])
                    if songs:
                        print(f"  [JioSaavn 320k] Found {len(songs)} songs via {sep[:30]}!")
                        top = songs[0]
                        t_str = str(top.get('name') or top.get('title'))
                        a_str = str(top.get('primaryArtists') or top.get('singers'))
                        d_urls = top.get('downloadUrl', [])
                        stream_url = d_urls[-1].get('url') if (isinstance(d_urls, list) and d_urls) else top.get('media_url')
                        print(f"     Title: '{t_str}' by '{a_str}'")
                        print(f"     320kbps MP3 URL: {str(stream_url)[:75]}...")
                        break
        except Exception as e:
            pass

    # 2. Test Deezer Master Stream
    try:
        url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            if res.status == 200:
                data = json.loads(res.read().decode('utf-8'))
                tracks = data.get('data', [])
                if tracks:
                    print(f"  [Deezer Master Stream] Found {len(tracks)} tracks!")
                    top = tracks[0]
                    t_str = str(top.get('title'))
                    a_str = str(top.get('artist', {}).get('name'))
                    preview_url = top.get('preview')
                    print(f"     Title: '{t_str}' by '{a_str}'")
                    print(f"     Preview Stream URL: {str(preview_url)[:75]}...")
    except Exception as e:
        pass
