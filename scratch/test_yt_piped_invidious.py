import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Test Piped, Invidious, and Cobalt APIs for YouTube Music stream resolution
queries = ["Coldplay Yellow", "Ed Sheeran Photograph", "Erie Suzan Senandung Rindu", "Denny Caknan Crito Mustahil"]

piped_instances = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.mha.fi",
    "https://api.piped.privacydev.net",
    "https://pipedapi.adminforge.de"
]

invidious_instances = [
    "https://inv.tux.pizza",
    "https://invidious.nerdvpn.de",
    "https://invidious.drgns.space",
    "https://yewtu.be"
]

print("=== 1. TESTING PIPED API SEARCH & AUDIO STREAMS ===")
for q in queries:
    print(f"\nQuery: '{q}'")
    found = False
    for p_inst in piped_instances:
        try:
            url = f"{p_inst}/search?q={urllib.parse.quote(q)}&filter=music_songs"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
                if res.status == 200:
                    data = json.loads(res.read().decode('utf-8'))
                    items = data.get('items', [])
                    print(f"  [{p_inst}] Found {len(items)} items!")
                    if items:
                        top = items[0]
                        v_id = top.get('url', '').replace('/watch?v=', '')
                        title = top.get('title', '').encode('ascii', 'ignore').decode('ascii')
                        uploader = top.get('uploaderName', '').encode('ascii', 'ignore').decode('ascii')
                        print(f"    -> Top YouTube Video: '{title}' by '{uploader}' (ID: {v_id})")
                        
                        # Fetch direct audio stream URL for this video ID!
                        s_url = f"{p_inst}/streams/{v_id}"
                        s_req = urllib.request.Request(s_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(s_req, timeout=5, context=ctx) as s_res:
                            if s_res.status == 200:
                                s_data = json.loads(s_res.read().decode('utf-8'))
                                audio_streams = s_data.get('audioStreams', [])
                                if audio_streams:
                                    top_audio = audio_streams[0]
                                    print(f"    ✅ DIRECT AUDIO STREAM FOUND! Bitrate: {top_audio.get('bitrate')}, Mime: {top_audio.get('mimeType')}")
                                    print(f"       Stream URL: {top_audio.get('url')[:80]}...")
                                    found = True
                                    break
        except Exception as e:
            # print(f"  Failed {p_inst}: {e}")
            pass
        if found:
            break

print("\n=== 2. TESTING INVIDIOUS API SEARCH & AUDIO STREAMS ===")
for q in queries:
    print(f"\nQuery: '{q}'")
    found = False
    for i_inst in invidious_instances:
        try:
            url = f"{i_inst}/api/v1/search?q={urllib.parse.quote(q)}&type=video"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5, context=ctx) as res:
                if res.status == 200:
                    items = json.loads(res.read().decode('utf-8'))
                    print(f"  [{i_inst}] Found {len(items)} items!")
                    if items:
                        top = items[0]
                        v_id = top.get('videoId')
                        title = top.get('title', '').encode('ascii', 'ignore').decode('ascii')
                        author = top.get('author', '').encode('ascii', 'ignore').decode('ascii')
                        print(f"    -> Top YouTube Video: '{title}' by '{author}' (ID: {v_id})")
                        
                        # Fetch video streams
                        v_url = f"{i_inst}/api/v1/videos/{v_id}"
                        v_req = urllib.request.Request(v_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(v_req, timeout=5, context=ctx) as v_res:
                            if v_res.status == 200:
                                v_data = json.loads(v_res.read().decode('utf-8'))
                                adaptive = v_data.get('adaptiveFormats', [])
                                audio_formats = [f for f in adaptive if 'audio' in f.get('type', '') or 'audio' in f.get('mimeType', '')]
                                if audio_formats:
                                    top_audio = audio_formats[0]
                                    print(f"    ✅ INVIDIOUS AUDIO STREAM FOUND! Bitrate: {top_audio.get('bitrate')}, Type: {top_audio.get('mimeType')}")
                                    print(f"       Stream URL: {top_audio.get('url')[:80]}...")
                                    found = True
                                    break
        except Exception as e:
            pass
        if found:
            break
