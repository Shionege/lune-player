import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = [
    ("Coldplay", "Yellow"),
    ("Ed Sheeran", "Photograph"),
    ("Erie Suzan", "Senandung Rindu"),
    ("Nasida Ria", "Bom Nuklir")
]

for artist, title in queries:
    print(f"\n================ Target: '{artist} - {title}' ================")
    # Format exact query for Archive.org
    q_str = f'title:("{title}") AND mediatype:(audio)'
    url = f"https://archive.org/advancedsearch.php?q={urllib.parse.quote(q_str)}&fl[]=identifier,title,creator,duration&rows=10&output=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            docs = data.get('response', {}).get('docs', [])
            print(f"  Archive docs count: {len(docs)}")
            for d in docs:
                ident = d.get('identifier')
                # Fetch metadata to verify full length mp3
                murl = f"https://archive.org/metadata/{ident}"
                mreq = urllib.request.Request(murl, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(mreq, timeout=4, context=ctx) as mres:
                    mdata = json.loads(mres.read().decode('utf-8'))
                    files = mdata.get('files', [])
                    mp3s = [f for f in files if f.get('name', '').endswith('.mp3')]
                    if mp3s:
                        full_mp3 = f"https://archive.org/download/{ident}/{urllib.parse.quote(mp3s[0]['name'])}"
                        print(f"  ✅ [FULL MP3 FOUND] Title: {d.get('title')} | Creator: {d.get('creator')} | File: {mp3s[0]['name']}")
                        print(f"     Direct URL: {full_mp3[:90]}...")
                        break
    except Exception as e:
        print(f"  Err: {e}")
