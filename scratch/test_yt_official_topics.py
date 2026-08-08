import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = [
    "Coldplay Yellow",
    "Ed Sheeran Photograph",
    "Ariana Grande hate that i made you love me",
    "Erie Suzan Senandung Rindu",
    "Denny Caknan Crito Mustahil",
    "Sheila on 7 Dan"
]

for q in queries:
    print(f"\n================ Target Query: '{q}' ================")
    # Query YouTube for "Topic" or "Official Audio"
    yt_query = f"{q} Official Audio"
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(yt_query)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            html = res.read().decode('utf-8')
            # Extract initial data JSON
            m = re.search(r'var ytInitialData = ({.+?});</script>', html) or re.search(r'window\["ytInitialData"\] = ({.+?});', html)
            if m:
                data = json.loads(m.group(1))
                contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                items = []
                for c in contents:
                    render = c.get('itemSectionRenderer', {}).get('contents', [])
                    for r in render:
                        vr = r.get('videoRenderer', {})
                        if vr:
                            vid = vr.get('videoId')
                            title = vr.get('title', {}).get('runs', [{}])[0].get('text')
                            owner = vr.get('ownerText', {}).get('runs', [{}])[0].get('text')
                            length = vr.get('lengthText', {}).get('simpleText')
                            items.append({'vid': vid, 'title': title, 'owner': owner, 'length': length})
                
                print(f"  YouTube Search Items found: {len(items)}")
                for it in items[:5]:
                    owner_name = str(it['owner'])
                    title_name = str(it['title'])
                    is_official = 'Topic' in owner_name or 'Official' in title_name or 'VEVO' in owner_name or 'Audio' in title_name
                    tag = "[100% ORIGINAL RECORDING]" if is_official else "[Other Video]"
                    print(f"  {tag} Title: '{title_name}' | Channel: '{owner_name}' | Length: {it['length']} | Vid: {it['vid']}")
    except Exception as e:
        print(f"  Error: {e}")
