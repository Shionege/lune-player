import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test Audiomack, Napster, Saavn, and Deezer stream providers
queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil", "Sheila on 7 Dan"]

print("=== TESTING AUDIOMACK, NAPSTER, SAAVN, DEEZER STREAMS ===")

for q in queries:
    print(f"\n================ Query: '{q}' ================")
    
    # 1. Test Saavn 320k
    try:
        url = f"https://saavn.dev/api/search/songs?query={urllib.parse.quote(q)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            songs = data.get('data', {}).get('results', []) or data.get('results', [])
            if songs:
                print(f"  ✅ [JioSaavn 320k] Found {len(songs)} songs!")
                top = songs[0]
                t_str = str(top.get('name') or top.get('title')).encode('ascii', 'ignore').decode('ascii')
                a_str = str(top.get('primaryArtists') or top.get('singers')).encode('ascii', 'ignore').decode('ascii')
                d_urls = top.get('downloadUrl', [])
                stream_url = d_urls[-1].get('url') if (isinstance(d_urls, list) and d_urls) else top.get('media_url')
                print(f"     Title: '{t_str}' by '{a_str}'")
                print(f"     320kbps MP3 URL: {str(stream_url)[:75]}...")
    except Exception as e:
        print(f"  Saavn error: {e}")

    # 2. Test Deezer Preview (320k 30s)
    try:
        url = f"https://api.deezer.com/search?q={urllib.parse.quote(q)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            tracks = data.get('data', [])
            if tracks:
                print(f"  ✅ [Deezer Master Stream] Found {len(tracks)} tracks!")
                top = tracks[0]
                t_str = str(top.get('title')).encode('ascii', 'ignore').decode('ascii')
                a_str = str(top.get('artist', {}).get('name')).encode('ascii', 'ignore').decode('ascii')
                preview_url = top.get('preview')
                print(f"     Title: '{t_str}' by '{a_str}'")
                print(f"     Preview Stream URL: {str(preview_url)[:75]}...")
    except Exception as e:
        print(f"  Deezer error: {e}")

    # 3. Test Audiomack Search
    try:
        url = f"https://api.audiomack.com/v1/search?q={urllib.parse.quote(q)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            results = data.get('results', [])
            if results:
                print(f"  ✅ [Audiomack] Found {len(results)} items!")
    except Exception as e:
        # print(f"  Audiomack error: {e}")
        pass
