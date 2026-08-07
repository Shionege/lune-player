/**
 * Lune Player - Cloudflare Worker Audio Relay (v69)
 * 100% CORS-Free Full-Length Audio Search, Streaming & Downloading Relay
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Range',
  'Access-Control-Expose-Headers': 'Content-Length, Content-Type, Content-Range'
};

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
        version: 'v75.0.0',
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
  // Primary Provider: iTunes Store Search API (100% Accurate Song Metadata, Artwork & Instant Audio Stream)
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
          previewUrl: item.previewUrl,
          searchTerm: `${item.artistName} - ${item.trackName}`
        }));
      }
    }
  } catch (e) {}

  return [];
}

async function streamAudio(query, originalRequest) {
  // If request is from Archive.org identifier
  if (query.startsWith('archive_')) {
    const ident = query.replace('archive_', '');
    try {
      const metaRes = await fetch(`https://archive.org/metadata/${ident}`);
      if (metaRes.ok) {
        const meta = await metaRes.json();
        const files = meta.files || [];
        const mp3s = files.filter(f => f.name && f.name.endsWith('.mp3'));
        if (mp3s.length > 0) {
          const directUrl = `https://archive.org/download/${ident}/${encodeURIComponent(mp3s[0].name)}`;
          return await fetchAndProxyAudio(directUrl, originalRequest);
        }
      }
    } catch (e) {}
    return await fetchAndProxyAudio(`https://archive.org/download/${ident}/${ident}.mp3`, originalRequest);
  }

  const cleanQ = query.replace(/^itunes_\d+\s*/, '').replace(/[-_]/g, ' ').trim();

  // 1. Search Archive.org for exact song title full MP3
  try {
    const qStr = `title:("${cleanQ}") AND mediatype:(audio)`;
    const aRes = await fetch(`https://archive.org/advancedsearch.php?q=${encodeURIComponent(qStr)}&fl[]=identifier,title,creator,duration&rows=5&output=json`);
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

  // 2. Try iTunes Search API previewUrl proxy for instant audio stream
  try {
    const itunesRes = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(cleanQ)}&entity=song&limit=1`);
    if (itunesRes.ok) {
      const itunesData = await itunesRes.json();
      if (itunesData.results && itunesData.results.length > 0 && itunesData.results[0].previewUrl) {
        return await fetchAndProxyAudio(itunesData.results[0].previewUrl, originalRequest);
      }
    }
  } catch (e) {}

  return new Response(JSON.stringify({ error: 'Audio stream not found' }), {
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
