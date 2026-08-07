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
        version: 'v69.0.0',
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
  let results = [];

  // 1. Try iTunes Search API (Official metadata & 600x600 artwork)
  try {
    const res = await fetch(`https://itunes.apple.com/search?term=${encodeURIComponent(query)}&entity=song&limit=20`);
    if (res.ok) {
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        results = data.results.map(item => ({
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

  // 2. Try Archive.org Search API
  try {
    const aRes = await fetch(`https://archive.org/advancedsearch.php?q=%28${encodeURIComponent(query)}%29+AND+mediatype%3A%28audio%29&fl[]=identifier,title,creator,duration&rows=10&output=json`);
    if (aRes.ok) {
      const aData = await aRes.json();
      const docs = aData.response?.docs || [];
      const aResults = docs.map(d => ({
        id: `archive_${d.identifier}`,
        title: d.title || query,
        artist: d.creator || 'Archive Audio',
        album: 'Public Music Archive',
        duration: Math.round(parseFloat(d.duration) || 210),
        thumbnail: `https://archive.org/services/img/${d.identifier}`,
        searchTerm: `${d.creator || ''} ${d.title || ''}`
      }));
      results = [...results, ...aResults];
    }
  } catch (e) {}

  return results;
}

async function streamAudio(query, originalRequest) {
  // If request is from Archive.org
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

  // Search Archive.org for full MP3 stream
  try {
    const aRes = await fetch(`https://archive.org/advancedsearch.php?q=%28${encodeURIComponent(query)}%29+AND+mediatype%3A%28audio%29&fl[]=identifier,title,creator,duration&rows=5&output=json`);
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
