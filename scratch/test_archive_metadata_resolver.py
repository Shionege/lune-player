import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

queries = ["Coldplay Yellow", "Alan Walker Faded", "Taylor Swift", "Lofi Beats", "Pop Music"]

for q in queries:
    print(f"\nSearching Archive.org: '{q}'")
    url = f"https://archive.org/advancedsearch.php?q=%28{urllib.parse.quote(q)}%29+AND+mediatype%3A%28audio%29&fl[]=identifier,title,creator,duration&rows=8&output=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            docs = data.get('response', {}).get('docs', [])
            for d in docs:
                ident = d.get('identifier')
                murl = f"https://archive.org/metadata/{ident}"
                mreq = urllib.request.Request(murl, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(mreq, timeout=4, context=ctx) as mres:
                    mdata = json.loads(mres.read().decode('utf-8'))
                    files = mdata.get('files', [])
                    mp3s = [f for f in files if f.get('name', '').endswith('.mp3')]
                    if mp3s:
                        full_mp3 = f"https://archive.org/download/{ident}/{urllib.parse.quote(mp3s[0]['name'])}"
                        print(f"  [SUCCESS] Title: '{d.get('title')}'")
                        print(f"            MP3: {full_mp3}")
                        
                        # Verify HTTP status & content length
                        hreq = urllib.request.Request(full_mp3, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
                        with urllib.request.urlopen(hreq, timeout=4, context=ctx) as hres:
                            print(f"            HTTP Status: {hres.status}, Content-Length: {hres.headers.get('Content-Length')}")
                        break
    except Exception as e:
        print("  Error:", e)
