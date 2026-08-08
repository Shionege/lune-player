import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil", "Sheila on 7 Dan"]

for q in queries:
    print(f"\n================ Multi-Provider Sound Test: '{q}' ================")
    
    # 1. Test Jamendo API Provider
    j_api = f"https://api.jamendo.com/v3.0/tracks/?client_id=56d306e9&format=json&limit=5&namesearch={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(j_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            results = data.get('results', [])
            print(f"  [Provider: Jamendo HQ MP3] Found: {len(results)} tracks")
            for r in results[:2]:
                title = r.get('name')
                artist = r.get('artist_name')
                audio_url = r.get('audio')
                dur = r.get('duration')
                print(f"    -> Title: '{title}' by '{artist}' ({dur}s) | Direct MP3: {audio_url[:70]}...")
    except Exception as e:
        print(f"  Jamendo error: {e}")

    # 2. Test JioSaavn / Saavn Me API Provider
    s_api = f"https://saavn.me/search/songs?query={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(s_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            results = data.get('data', {}).get('results', [])
            print(f"  [Provider: Saavn.me 320kbps Engine] Found: {len(results)} tracks")
            for r in results[:2]:
                title = r.get('name')
                artist = r.get('primaryArtists')
                d_urls = r.get('downloadUrl', [])
                if d_urls:
                    print(f"    -> Title: '{title}' by '{artist}' | Direct 320kbps MP3: {d_urls[-1].get('url')[:70]}...")
    except Exception as e:
        print(f"  Saavn error: {e}")
        
    # 3. Test Internet Archive Audio Vault Provider
    a_api = f"https://archive.org/advancedsearch.php?q=%28{urllib.parse.quote(q)}%29+AND+mediatype%3A%28audio%29&fl[]=identifier,title,creator,duration&rows=3&output=json"
    try:
        req = urllib.request.Request(a_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            docs = data.get('response', {}).get('docs', [])
            print(f"  [Provider: Internet Archive Vault] Found: {len(docs)} tracks")
            for d in docs[:2]:
                print(f"    -> Title: '{d.get('title')}' by '{d.get('creator')}' ({d.get('duration')}s)")
    except Exception as e:
        print(f"  Archive error: {e}")
