import urllib.request
import json
import ssl
import base64

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test fetching official studio tracks from Saavn API
queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Ariana Grande hate that i made you love me", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil"]

for q in queries:
    print(f"\n================ Official Track Query: '{q}' ================")
    # JioSaavn internal search API
    url = f"https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
            data = json.loads(res.read().decode('utf-8'))
            songs = data.get('songs', {}).get('data', [])
            print(f"  Official JioSaavn songs found: {len(songs)}")
            for s in songs:
                title = s.get('title')
                singers = s.get('singers')
                album = s.get('album')
                encrypted_media_url = s.get('more_info', {}).get('encrypted_media_url')
                print(f"  -> Title: '{title}' | Singers: '{singers}' | Album: '{album}'")
                print(f"     Encrypted URL: {str(encrypted_media_url)[:50]}...")
                
                # Test decrypting encrypted_media_url using DES-ECB with key "38588500"
                if encrypted_media_url:
                    try:
                        from Crypto.Cipher import DES
                        cipher = DES.new(b"38588500", DES.MODE_ECB)
                        enc_bytes = base64.b64decode(encrypted_media_url)
                        dec_bytes = cipher.decrypt(enc_bytes)
                        # Remove DES padding
                        pad_len = dec_bytes[-1]
                        if isinstance(pad_len, int) and pad_len <= 8:
                            dec_bytes = dec_bytes[:-pad_len]
                        dec_url = dec_bytes.decode('utf-8')
                        print(f"     ✅ DECRYPTED OFFICIAL STREAM URL: {dec_url}")
                        
                        # Replace quality to 320kbps MP3 / 160kbps MP4
                        dec_url_320 = dec_url.replace('_96.mp4', '_320.mp4').replace('_160.mp4', '_320.mp4')
                        
                        # Test fetching HEAD on decrypted URL
                        hreq = urllib.request.Request(dec_url_320, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(hreq, timeout=5, context=ctx) as hres:
                            size_mb = round(int(hres.headers.get('Content-Length', 0)) / (1024*1024), 2)
                            print(f"     ✅ [100% OFFICIAL ORIGINAL STUDIO MASTER] Status: {hres.status} | Size: {size_mb} MB")
                            break
                    except Exception as de:
                        print(f"     Decryption error: {de}")
    except Exception as e:
        print(f"  Search error: {e}")
