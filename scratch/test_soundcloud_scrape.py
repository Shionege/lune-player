import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test scraping SoundCloud search for direct MP3 / HLS audio streams
queries = ["Ed Sheeran Photograph", "Coldplay Yellow", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir"]

for q in queries:
    print(f"\n================ SoundCloud test: '{q}' ================")
    # Search SoundCloud via public widget/client id or direct search page HTML
    sc_search = f"https://soundcloud.com/search/sounds?q={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(sc_search, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            html = res.read().decode('utf-8')
            # Extract client_id or track URLs
            links = re.findall(r'href="(/[^/]+/[^"]+)"', html)
            sound_links = [l for l in links if not l.startswith('/search') and not l.startswith('/pages') and not l.startswith('/terms')]
            print(f"  SoundCloud track links found: {sound_links[:3]}")
    except Exception as e:
        print(f"  SoundCloud error: {e}")
