/**
 * Lune Player - Cloudflare Worker Audio Relay (v79.0.0)
 * 100% CORS-Free Full-Length Audio Search, Streaming & Downloading Relay
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Range',
  'Access-Control-Expose-Headers': 'Content-Length, Content-Type, Content-Range'
};

let scClientIdCache = 'TwElDfIgW9RpAzLMUSy9g1VvI2Kao7my';

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const pathname = url.pathname;

    try {
      if (pathname === '/search' || pathname === '/search/') {
        const query = url.searchParams.get('q') || 'Indonesia Top Hits';
        const results = await searchAudio(query);
        return new Response(JSON.stringify({ status: true, results }), {
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
        });
      }

      if (pathname === '/audio' || pathname === '/audio/') {
        const query = url.searchParams.get('q') || url.searchParams.get('id') || '';
        const audioRes = await streamAudio(query, request);
        return audioRes;
      }

      // Root info page
      return new Response(JSON.stringify({
        app: 'Lune Player Audio Relay',
        version: 'v80.0.0',
        status: 'Active',
        endpoints: ['/search?q=query', '/audio?q=query']
      }), {
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    } catch (err) {
      return new Response(JSON.stringify({ status: false, error: err.message }), {
        status: 500,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    }
  }
};

async function searchAudio(query) {
  // Primary Provider: Official iTunes Search API for 100% Accurate Song Metadata & 600x600 Artwork
  try {
    const res = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(query)}&entity=song&limit=30`);
    if (res.ok) {
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        return data.results.map(item => ({
          id: `itunes_${item.trackId}`,
          title: item.trackName,
          artist: item.artistName || 'Various Artists',
          album: item.collectionName || 'Single',
          duration: Math.round((item.trackTimeMillis || 180000) / 1000),
          thumbnail: item.artworkUrl100 ? item.artworkUrl100.replace('100x100bb', '600x600bb') : item.artworkUrl60,
          searchTerm: `${item.artistName} - ${item.trackName}`
        }));
      }
    }
  } catch (e) {}

  return [];
}

async function getSoundCloudClientId() {
  if (scClientIdCache) return scClientIdCache;
  try {
    const res = await fetch('https://soundcloud.com', {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
    });
    if (res.ok) {
      const html = await res.text();
      const jsMatches = [...html.matchAll(/src="(https:\/\/a-v2\.sndcdn\.com\/assets\/[^"]+\.js)"/g)];
      for (const m of jsMatches.reverse().slice(0, 3)) {
        const jres = await fetch(m[1]);
        if (jres.ok) {
          const jtext = await jres.text();
          const cids = jtext.match(/client_id[:=]"([a-zA-Z0-9]{32})"/);
          if (cids) {
            scClientIdCache = cids[1];
            return scClientIdCache;
          }
        }
      }
    }
  } catch (e) {}
  return 'TwElDfIgW9RpAzLMUSy9g1VvI2Kao7my';
}

async function streamAudio(query, originalRequest) {
  const cleanQ = query.replace(/^itunes_\d+\s*/, '').replace(/[-_]/g, ' ').trim();
  if (!cleanQ) {
    return new Response(JSON.stringify({ error: 'Query parameter is empty' }), {
      status: 400,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
    });
  }

  // 1. Primary Engine: SoundCloud Full-Length Audio Stream Extractor (Duration > 100 seconds)
  try {
    const cid = await getSoundCloudClientId();
    const scApi = `https://api-v2.soundcloud.com/search/tracks?q=${encodeURIComponent(cleanQ)}&client_id=${cid}&limit=10`;
    const scRes = await fetch(scApi, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
    });
    if (scRes.ok) {
      const scData = await scRes.json();
      const tracks = scData.collection || [];
      for (const tr of tracks) {
        // Must be full track (> 100 seconds)
        if (tr.duration && tr.duration > 100000) {
          const media = tr.media?.transcodings || [];
          const prog = media.find(m => m.format?.protocol === 'progressive');
          if (prog) {
            const streamApi = `${prog.url}?client_id=${cid}`;
            const sRes = await fetch(streamApi, {
              headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
            });
            if (sRes.ok) {
              const sData = await sRes.json();
              if (sData.url) {
                return await fetchAndProxyAudio(sData.url, originalRequest);
              }
            }
          }
        }
      }
    }
  } catch (e) {}

  // 2. Secondary Engine: Archive.org Exact Title Search
  try {
    const aRes = await fetch(`https://archive.org/advancedsearch.php?q=%28${encodeURIComponent(cleanQ)}%29+AND+mediatype%3A%28audio%29&fl[]=identifier,title,creator,duration&rows=5&output=json`);
    if (aRes.ok) {
      const aData = await aRes.json();
      const docs = aData.response?.docs || [];
      for (const d of docs) {
        const metaRes = await fetch(`https://archive.org/metadata/${d.identifier}`);
        if (metaRes.ok) {
          const meta = await metaRes.json();
          const mp3s = (meta.files || []).filter(f => f.name && f.name.endsWith('.mp3'));
          if (mp3s.length > 0) {
            const streamUrl = `https://archive.org/download/${d.identifier}/${encodeURIComponent(mp3s[0].name)}`;
            return await fetchAndProxyAudio(streamUrl, originalRequest);
          }
        }
      }
    }
  } catch (e) {}

  return new Response(JSON.stringify({ error: 'Full length audio stream not found' }), {
    status: 404,
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
  });
}

async function fetchAndProxyAudio(audioUrl, originalRequest) {
  const reqHeaders = new Headers();
  const range = originalRequest.headers.get('Range');
  if (range) reqHeaders.set('Range', range);
  reqHeaders.set('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)');

  const response = await fetch(audioUrl, { headers: reqHeaders });

  const resHeaders = new Headers(CORS_HEADERS);
  const passHeaders = ['content-type', 'content-length', 'content-range', 'accept-ranges'];
  for (const h of passHeaders) {
    if (response.headers.has(h)) {
      resHeaders.set(h, response.headers.get(h));
    }
  }

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: resHeaders
  });
}
