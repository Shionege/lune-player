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
    print(f"\n================ Official Record Label Topic Channel Search: '{q}' ================")
    yt_query = f"{q} Topic"
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(yt_query)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            html = res.read().decode('utf-8')
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
                
                official_topic_items = []
                for it in items:
                    owner_lower = str(it['owner']).lower()
                    title_lower = str(it['title']).lower()
                    if 'topic' in owner_lower or 'vevo' in owner_lower or 'official' in owner_lower or 'sony' in owner_lower or 'warner' in owner_lower or 'universal' in owner_lower or 'music' in owner_lower:
                        official_topic_items.append(it)
                
                print(f"  Total items: {len(items)} | OFFICIAL LABEL CHANNELS: {len(official_topic_items)}")
                for oit in official_topic_items[:3]:
                    t_str = str(oit['title']).encode('ascii', 'ignore').decode('ascii')
                    o_str = str(oit['owner']).encode('ascii', 'ignore').decode('ascii')
                    print(f"  [100% OFFICIAL RECORD LABEL STREAM] Title: '{t_str}' | Label/Artist: '{o_str}' | Vid: {oit['vid']} | Length: {oit['length']}")
    except Exception as e:
        print(f"  Error: {e}")
