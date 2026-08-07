import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Nasida Ria Bom Nuklir", "Denny Caknan Crito Mustahil"]

for q in queries:
    print(f"\nSearch: {q}")
    url = f"https://archive.org/advancedsearch.php?q=%28{urllib.parse.quote(q)}%29+AND+mediatype%3A%28audio%29&fl[]=identifier,title,creator,duration&rows=3&output=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            docs = data.get('response', {}).get('docs', [])
            for d in docs:
                ident = d.get('identifier')
                meta_url = f"https://archive.org/metadata/{ident}"
                mreq = urllib.request.Request(meta_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(mreq, timeout=4, context=ctx) as mres:
                    mdata = json.loads(mres.read().decode('utf-8'))
                    files = mdata.get('files', [])
                    mp3s = [f for f in files if f.get('name', '').endswith('.mp3')]
                    if mp3s:
                        full_mp3 = f"https://archive.org/download/{ident}/{urllib.parse.quote(mp3s[0]['name'])}"
                        print(f"  -> Title: {d.get('title')} | Duration: {d.get('duration')}s | URL: {full_mp3[:80]}...")
    except Exception as e:
        print("  Error:", e)
