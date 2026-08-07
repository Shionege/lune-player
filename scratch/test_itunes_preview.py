import urllib.request
import json

url = "https://itunes.apple.com/search?term=Erie+Suzan+Senandung+Rindu&entity=song&limit=5"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=5) as res:
    data = json.loads(res.read().decode('utf-8'))
    for item in data.get('results', []):
        print("Title:", item.get('trackName'))
        print("Artist:", item.get('artistName'))
        print("Preview URL:", item.get('previewUrl'))
        print("---")
