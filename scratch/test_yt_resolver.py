import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir"]

for q in queries:
    print(f"\n================ Target: '{q}' ================")
    url = "https://itunes.apple.com/search?term=" + urllib.parse.quote(q) + "&entity=song&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
        item = json.loads(res.read().decode('utf-8'))['results'][0]
        artist = item['artistName']
        title = item['trackName']
        print(f"iTunes Track: {artist} - {title}")
        
        # Test YouTube search query HTML parsing via CORS-proxy / API
        yt_search = f"https://www.youtube.com/results?search_query={urllib.parse.quote(artist + ' ' + title + ' audio')}"
        yreq = urllib.request.Request(yt_search, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            with urllib.request.urlopen(yreq, timeout=5, context=ctx) as yres:
                html = yres.read().decode('utf-8')
                if 'videoId' in html:
                    import re
                    vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                    print(f"  -> YouTube Video IDs found: {list(set(vids))[:3]}")
        except Exception as e:
            print(f"  -> YouTube search error: {e}")
